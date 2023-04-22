JSONPrimitive = str | int | float | bool | None
JSONValue = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
JSONObject = dict[str, JSONValue]

BooruJSON = (
    dict[str, JSONPrimitive] | dict[str, dict[str, JSONPrimitive] | JSONPrimitive] | list[dict[str, JSONPrimitive]]
)
