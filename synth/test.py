var = ["hi", "no"]

match var:
    case ("hi", *sublevels):
        print("hi")
        match sublevels:
            case ["ok"]:
                print("ok")
            case ["no"]:
                print("o")
    case _:
        print("no")