from fastapi.responses import JSONResponse

class RestResponse:
    def __init__(self, data=None, message="", error=""):
        self.data=data
        self.message = message
        self.error = error

    def to_json(self):
        return JSONResponse(self.__dict__)
    

   
    

        