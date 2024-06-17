class ResponseModel():
    def __init__(self, response: str, sources: str, send_pdf: bool):
        self.response = response
        self.sources = sources
        self.send_pdf = send_pdf