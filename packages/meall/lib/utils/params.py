from cnoc.params import AllParamModelTypes, Params


def Params2ParamModels(params: Params):
    res: ParamModels = {}
    for [name, param] in params.items():
        res[name] = param.toBaseModel()

    return res


type ParamModels = dict[str, AllParamModelTypes]


def ParamModels2Params(param_models: ParamModels):
    res: Params = {}
    for [name, param_model] in param_models.items():
        res[name] = param_model.toParam()

    return res


def experimentParams2Backup(experiment_id: str, params: Params):
    res: dict[str, dict[str, str]] = {"experiment_id": experiment_id}

    def parseParams(id: str, params: Params):
        if id in res:
            return

        res[id] = {}

        for [name, param] in params.items():
            res[experiment_id][name] = param.getValue()

            # If the param is an instance, recursively parse the params as well
            if (
                param._type == "instance.equipment"
                or param._type == "instance.experiment"
            ):
                if param.instance is not None:
                    parseParams(param._instance_id, param.instance.params)

    parseParams(experiment_id, params)

    return res
