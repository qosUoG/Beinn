from typing import Enum

class ParamType(Enum):
    Arange = "Arange"
    Linspace = "Linspace"
    Str = "Str"
    Int = "Int"
    Float = "Float"
    
    @classmethod
    def ArangeParam(cls, name: str):
        return {
            "name": name,
            "tp": ParamType.Arange
        }
        

    
    

        
        
        
            
            