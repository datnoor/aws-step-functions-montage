import json


class StepFunctionsDagConverter:
    def __init__(self):
        self.result = None
        self.data = {}
        self.names = []
        self.executables = []
        self.args = []
        self.inputs = []
        self.outputs = []

    def load(self, filename):
        with open(filename, "r") as json_file:
            dag_json = json.load(json_file)
            self.data = dag_json["data"]
            self.names = [x["name"] for x in dag_json["tasks"]]
            self.executables = [x["config"]["executor"]["executable"] for x in dag_json["tasks"]]
            self.args = [x["config"]["executor"]["args"] for x in dag_json["tasks"]]
            self.inputs = [x["ins"] for x in dag_json["tasks"]]
            self.outputs = [x["outs"] for x in dag_json["tasks"]]

    def save(self, filename):
        with open(filename, "w+") as json_file:
            json_file.write(json.dumps(self.result, indent=2, sort_keys=True))

    def _next_name(self, _index):
        this_name = self.names[_index]
        for _name in self.names[_index:]:
            if _name != this_name:
                return _name
        return "Final State"

    def _data(self, _indexes):
        _result = []
        for _index in _indexes:
            _result.append(self.data[_index])
        return _result

    def _branch_dict(self, name, index, counter):
        branch_dict = {
            "StartAt": name + str(counter),
            "States": {
                name + str(counter): {
                    "Type": "Pass",
                    "Result": {
                        "body": {
                            "executable": self.executables[index],
                            "args": self.args[index],
                            "inputs": self._data(self.inputs[index]),
                            "outputs": self._data(self.outputs[index]),
                            "options": {
                                "storage": "s3",
                                "bucket": "montage-lambda",
                                "prefix": "data/0.025/input"
                            }
                        }
                    },
                    "Next": name + "Task" + str(counter)
                },
                name + "Task" + str(counter): {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:eu-west-1:217740368147:function:hyperflowExecutor2",
                    "End": True
                }
            }
        }
        return branch_dict

    def convert(self):
        states = {}
        counter = 1
        names_number = len(self.names)
        for index, name in enumerate(self.names):
            if index == 0 or name != self.names[index - 1]:
                list_of_branches = []
                counter = 1
                project_dict = {"Type": "Parallel", "Next": self._next_name(index)}
                branch_dict = self._branch_dict(name, index, counter)
                list_of_branches.append(branch_dict.copy())
            else:
                counter += 1
                branch_dict = self._branch_dict(name, index, counter)
                list_of_branches.append(branch_dict.copy())

            if index == names_number - 1:
                project_dict["Branches"] = list_of_branches
                states[name] = project_dict
                states["Final State"] = {
                    "Type": "Pass",
                    "End": True
                }
            elif name != self.names[index + 1]:
                project_dict["Branches"] = list_of_branches
                states[name] = project_dict

        self.result = {"Comment": "", "StartAt": self.names[0], "States": states}
        return self.result


def main():
    converter = StepFunctionsDagConverter()
    converter.load("./data/0.1/workdir/dag.json")
    converter.convert()
    converter.save("./sf.json")

if __name__ == "__main__":
    main()
