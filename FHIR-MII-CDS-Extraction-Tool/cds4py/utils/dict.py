class Dict:
    @staticmethod
    def flatten(resource_dict):
        out = {}

        def flatten(x, name=""):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + str(a) + "_")
            elif type(x) is list:
                i = 0
                for a in x:
                    if type(a) is dict:
                        flatten(a, name + str(i) + "_")
                    else:
                        out[name + str(i)] = a
                        i += 1
            else:
                out[name[:-1]] = x

        flatten(resource_dict)
        return out
