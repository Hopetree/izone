class OpenCode:
    # 函数执行超时，例如函数执行 requests 请求超时
    error_50000 = 50000
    # 函数执行错误，一般是未知异常，此时可以打印异常去定位原因
    error_50001 = 50001
    # 函数返回内容不合法，例如请求到的内容不符合返回体结构
    error_50002 = 50002


class OpenApi(OpenCode):
    code = 0
    error = ""
    message = ""
    data = {}

    @property
    def body(self):
        resp = {
            "code": self.code,  # 业务返回码，非0失败
            "error": self.error,  # 错误提示，面向用户
            "message": self.message,  # 错误提示，面向开发者
            "data": self.data  # 返回数据，字典
        }
        return resp


if __name__ == '__main__':
    op = OpenApi()
    op.code = 1
    op.data = [{"name": "izone"}]
    print(op.body)
    print(op.error_50000)
