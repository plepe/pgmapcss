class config_eval_XML_encode(config_base):
    mutable = 3

def eval_XML_encode(param):
    if len(param) == 0:
        return ''

    v = param[0]

    v = v.replace("&", "&amp;")
    v = v.replace("<", "&lt;")
    v = v.replace(">", "&gt;")
    v = v.replace("\"", "&quot;")
    v = v.replace("\'", "&apos;")

    return v

# TESTS
# IN [ '<foo>&</foo>' ]
# OUT '&lt;foo&gt;&amp;&lt;/foo&gt;'
