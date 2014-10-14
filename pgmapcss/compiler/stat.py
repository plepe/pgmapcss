import pgmapcss.types
import pgmapcss.eval
import copy

class _stat(dict):
    property_values_cache = {}

    def clear_property_values_cache(self):
        self.property_values_cache = {}

    def all_scale_denominators(self):
        return sorted(list(set([
                v['selector']['min_scale']
                for v in self['statements']
            ] + \
            [
                v['selector']['max_scale']
                for v in self['statements']
                if v['selector']['max_scale'] != None
            ])),
            reverse=True)

    def properties(self, pseudo_element=None, max_prop_id=None, object_type=None):
        ret = set([
            p['key']
            for v in self['statements']
            if object_type is None or v['selector']['type'] == object_type
            if pseudo_element == None or v['selector']['pseudo_element'] in ('*', p)
            for p in v['properties']
            if p['assignment_type'] == 'P'
            if max_prop_id is None or p['id'] <= max_prop_id
        ])

        if max_prop_id is None or 'default_value' in stat['defines']:
            for k in self['defines']['default_value']:
                ret.add(k)

        return ret

    def property_default_value(self, prop):
        if 'default_other' in self['defines'] and prop in self['defines']['default_other']:
            other = self['defines']['default_other'][prop]['value']
            if other:
                value = self.property_default_value(other)
                if value is not None:
                    return value

        if 'default_value' in self['defines'] and prop in self['defines']['default_value']:
            value = self['defines']['default_value'][prop]['value']
            if value is not None:
                return value

        return None


    def property_values(self, prop, pseudo_element=None, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None, include_none=False, object_type=None, postprocess=True, warn_unresolvable=False):
        """Returns set of all values used on this property in any statement.
        Returns boolean 'True' if property is result of an unresolveable eval
        expression.

        Parameters:
        pseudo_element: limit returned values to given pseudo_element (default: None which means all)
        include_illegal_values: If True all values as given in MapCSS are returned, if False the list is sanitized (see @values). (Forces include_none=True) Default: False
        include_none: If True, None is a possible value (if used). Default: False
        value_type: Only values with value_type will be returned. Default None (all)
        eval_true: Return 'True' for values which result of an unresolvable eval expression. Otherwise this value will be removed. Default: True.
        max_prop_id: evaluate only properties with an id <= max_prop_id
        object_type: return values only for given object type (e.g. 'canvas')
        postprocess: include values derived from postprocessing
        warn_unresolvable: warn, if the property might be unresolvable
        """
        # Don't need 'eval_true' and 'warn_unresolvable' in cache_id, will be handled specially
        cache_id = prop + '-' + repr(pseudo_element) + '-' + repr(include_illegal_values) + '-' + repr(value_type) + '-' + repr(max_prop_id) + '-' + repr(include_none) + '-' + repr(object_type) + '-' + repr(postprocess)

        # Check if values are already calculated in cache
        if cache_id in self.property_values_cache:
            values = self.property_values_cache[cache_id]

            if warn_unresolvable and True in values:
                if not 'unresolvable_properties' in self:
                    self['unresolvable_properties'] = set()
                self['unresolvable_properties'].add(prop)

            if not eval_true and True in values:
                values = copy.copy(values)
                values.remove(True)

            return values

        prop_type = pgmapcss.types.get(prop, self)

        # go over all statements and their properties and collect it's values. If
        # include_illegal_values==False sanitize list. Do not include eval
        # statements.
        values = {
            p['value'] if include_illegal_values else prop_type.stat_value(p)
            for v in self['statements']
            for p in v['properties']
            if object_type is None or v['selector']['type'] == object_type
            if pseudo_element == None or v['selector']['pseudo_element'] in ('*', pseudo_element)
            if p['assignment_type'] == 'P' and p['key'] == prop
            if value_type == None or value_type == p['value_type']
            if p['value_type'] != 'eval'
            if max_prop_id is None or p['id'] <= max_prop_id
        }

        # resolve eval functions (as far as possible) - also sanitize list.
        if True:
            values = values.union({
                v1 if v1 == True or include_illegal_values else prop_type.stat_value({
                    'value_type': 'eval',
                    'value': v1
                })
                for v in self['statements']
                for p in v['properties']
                if pseudo_element == None or v['selector']['pseudo_element'] in ('*', pseudo_element)
                if p['assignment_type'] == 'P' and p['key'] == prop
                if p['value_type'] == 'eval'
                if max_prop_id is None or p['id'] <= max_prop_id
                for v1 in pgmapcss.eval.possible_values(p['value'], p, self)[0]
            })

        if 'default_value' in self['defines'] and prop in self['defines']['default_value']:
            v = self['defines']['default_value'][prop]['value']
            if include_illegal_values or v is not None:
                values.add(v)

        if 'default_other' in self['defines'] and prop in self['defines']['default_other']:
            other = self['defines']['default_other'][prop]['value']
            if other:
                other = self.property_values(other, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id)
                values = values.union(other)

        if 'generated_properties' in self and prop in self['generated_properties']:
            gen = self['generated_properties'][prop]
            combinations = self.properties_combinations(gen[0], pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id, include_none, warn_unresolvable)
            values = values.union({
                gen[1](combination, self)
                for combination in combinations
            })

        if postprocess and 'postprocess' in self['defines'] and prop in self['defines']['postprocess'] and max_prop_id is None:
            p = copy.copy(self['defines']['postprocess'][prop])
            p['id'] = self['max_prop_id'] + 1
            for pe in ([pseudo_element] if pseudo_element else self['pseudo_elements']):
                p['statement'] = { 'selector': { 'pseudo_element': pe }}
                v = pgmapcss.eval.possible_values(p['value'], p, self)[0]
                values = values.union(v)

        if postprocess:
            v = prop_type.stat_postprocess(values, pseudo_element=pseudo_element)
            if v:
                values = v

        if include_illegal_values:
            self.property_values_cache[cache_id] = values
            return values

        if True in values:
            values.remove(True)
            values = values.union(prop_type.stat_all_values())

        if not include_none:
            values = {
                v
                for v in values
                if v != None
            }

        if warn_unresolvable and True in values:
            if not 'unresolvable_properties' in self:
                self['unresolvable_properties'] = set()
            self['unresolvable_properties'].add(prop)

        self.property_values_cache[cache_id] = values

        if not eval_true and True in values:
            values = copy.copy(values)
            values.remove(True)

        return values

    def properties_combinations_pseudo_element(self, keys, pseudo_element, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None, include_none=False, warn_unresolvable=False):
        combinations_list = [{}]

        for k in keys:
            new_combinations_list = []

            for combination in combinations_list:
                for v in self.property_values(k, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id, include_none, warn_unresolvable=warn_unresolvable):
                    c = combination.copy()
                    c[k] = v
                    new_combinations_list.append(c)

            combinations_list = new_combinations_list

        return combinations_list

    def properties_combinations(self, keys, pseudo_elements=None, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None, include_none=False, warn_unresolvable=False):
        combinations = []
        if type(pseudo_elements) == str:
            pseudo_elements = [ pseudo_elements ]
        if pseudo_elements is None:
            pseudo_elements = self['pseudo_elements']

        for pseudo_element in pseudo_elements:
            combinations += self.properties_combinations_pseudo_element(keys, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id, include_none, warn_unresolvable)

        ret = []
        for combination in combinations:
            if not combination in ret:
                ret += [ combination ]

        return ret

    def add_generated_property(self, key, keys, fun):
        if not 'generated_properties' in self:
            self['generated_properties'] = {}

        self['generated_properties'][key] = ( keys, fun )

    def _has_set_tag(self, statement, key):
        # JOSM classes ("set foo" => set ".foo" too)
        key_no_dot = False
        if self['config'].get('josm_classes', '') == 'true' \
          and key[0] == '.':
            key_no_dot = key[1:]

        for prop in statement['properties']:
            if prop['assignment_type'] == 'T' and prop['key'] == key:
                return True

            # JOSM classes ("set foo" => set ".foo" too)
            if key_no_dot and prop['assignment_type'] == 'T' and prop['key'] == key_no_dot:
                return True

        return False

    def filter_statements(self, filter):
        return [
            statement
            for statement in self['statements']
            if not 'min_scale' in filter or statement['selector']['min_scale'] <= filter['min_scale']
            if not 'max_scale' in filter or filter['max_scale'] == None or statement['selector']['max_scale'] == None or statement['selector']['max_scale'] >= filter['max_scale']
            if not 'max_id' in filter or statement['id'] <= filter['max_id']
            if not 'has_set_tag' in filter or self._has_set_tag(statement, filter['has_set_tag'])
            if not 'object_type' in filter or statement['selector']['type'] in (True, filter['object_type'])
        ]
