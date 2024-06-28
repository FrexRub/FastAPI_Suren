import jwt

encoded = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")

decodet = jwt.decode(encoded, "secret", algorithms=["HS256"])