class config_eval_style_id(config_base):
    def compiler(self, param, eval_param, stat):
        return repr(stat['id']);
