from fastapi.responses import JSONResponse

class RestResponse:
    def __init__(self, data=None, message="", error="",metadata = {}):
        self.data=data
        self.message = message
        self.error = error
        self.metadata = metadata

    def to_json(self):
        return JSONResponse(self.__dict__)
    

   
    

        