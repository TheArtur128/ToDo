from act import type


type Page = str
type Message = str

LazyPage = type(template=str, context=dict)
Mail = type(title=Message, message=Message, page=Page)
