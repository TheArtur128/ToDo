from act import Unia


type Sculpture[FormT, OriginalT] = (
    Unia[FormT, type(_sculpture_original=OriginalT)]
)
