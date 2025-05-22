from __future__ import annotations
import aiohttp
import asyncio
import uvloop
from avndb.exceptions import *
import datetime
import typing as t
from dataclasses import dataclass, field

NOT_INITIALIZED: t.Final = "VNDBClient not initialized"

@dataclass(slots=True, frozen=True)
class VNDBUser:
    id: str
    username: str
    lengthvotes: t.Optional[int] = None
    lengthvotes_sum: t.Optional[int] = None

@dataclass(slots=True, frozen=True)
class VNDBAuthInfo:
    id: str
    username: str
    permissions: t.Optional[t.List[str]] = None

@dataclass(slots=True, frozen=True)
class VNDBStats:
    chars: int
    producers: int
    releases: int
    staff: int
    tags: int
    traits: int
    vn: int

@dataclass(slots=True)
class VNDBFilter:
    """
    Filter object for VNDB database queries. Only works with `POST` requests.
    
    Attributes:
        lang (Optional[List[str]]): A list of languages to filter by. Use the country's abbreviation code (e.g. `en`, `ja`, `fr`, `de`, etc.). Defaults to an empty list.
        olang (Optional[List[str]]): A list of original (the original language of the VN) languages to filter by. Use the country's abbreviation code (e.g. `en`, `ja`, `fr`, `de`, etc.). Defaults to an empty list.
        releasedBefore (Optional[str]):
            A string representing the date before which the VN was released. 
            This filter is used to find VNs released before a certain date. The format
            must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised.
            Defaults to an empty string.
        releasedAfter (Optional[str]):
            See `releaseBefore`. This filter is used to find VNs released *after* a certain date. The format
            must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised. Defaults to an empty string.
        releasedOn (Optional[str]):
            See `releasedBefore` and `releasedAfter`. This filter is used to find VNs release on a certain date.
            The format must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised. Defaults to an empty string.
        producers (Optional[List[str]]):
            A list of producers to filter by. Use the producer's VNDB ID (See [Common Data Types](https://api.vndb.org/kana#common-data-types)). Defaults to an empty list.
    """
    lang: t.Optional[t.List[str]] = field(default_factory=list)
    olang: t.Optional[t.List[str]] = field(default_factory=list)
    releasedBefore: t.Optional[str] = field(default_factory=str)
    """A string representing the date before which the VN was released. 
            This filter is used to find VNs released before a certain date. The format
            must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised.
            Defaults to an empty string."""
    releasedAfter: t.Optional[str] = field(default_factory=str)
    """See `releaseBefore`. This filter is used to find VNs released *after* a certain date. The format
            must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised. Defaults to an empty string."""
    releasedOn: t.Optional[str] = field(default_factory=str)
    """See `releasedBefore` and `releasedAfter`. This filter is used to find VNs release on a certain date.
            The format must be in the `YYYY-MM-DD` format, otherwise `IllformedVNDBQuery` will be raised. Defaults to an empty string."""
    producers: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of producers to filter by. Use the producer's VNDB ID (See [Common Data Types](https://api.vndb.org/kana#common-data-types)). Defaults to an empty list."""   

    # Check if the date is in the YYYY-MM-DD format.
    def __post_init__(self) -> None:
        if self.releasedBefore:
            try:
                datetime.datetime.strptime(self.releasedBefore, "%Y-%m-%d")
            except ValueError:
                raise IllformedVNDBQuery("releasedBefore must be in the YYYY-MM-DD format and must be a valid date.")
        if self.releasedAfter:
            try:
                datetime.datetime.strptime(self.releasedAfter, "%Y-%m-%d")
            except ValueError:
                raise IllformedVNDBQuery("releasedAfter must be in the YYYY-MM-DD format and must be a valid date.")
        if self.releasedOn:
            try:
                datetime.datetime.strptime(self.releasedOn, "%Y-%m-%d")
            except ValueError:
                raise IllformedVNDBQuery("releasedOn must be in the YYYY-MM-DD format and must be a valid date.")

@dataclass(slots=True)
class VNFilter:
    """A filter object for VN `POST` queries."""
    id: t.Optional[str] = field(default_factory=str)
    """See [Common Data Types](https://api.vndb.org/kana#common-data-types). The VNDB ID of the VN. Defaults to an empty string."""
    lang: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of languages to filter by. Use the country's abbreviation code (e.g. `en`, `ja`, `fr`, `de`, etc.). Defaults to an empty list."""
    olang: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of original (the original language of the VN) languages to filter by. Use the country's abbreviation code (e.g. `en`, `ja`, `fr`, `de`, etc.). Defaults to an empty list."""
    platform: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of platforms to filter by. Defaults to an empty list."""
    released: t.Optional[Released] = None
    """A Released object representing the release date of the VN. Defaults to None."""
    length: t.Optional[Length] = None
    """See :attr:`VN.length`. A Length object representing the length of the VN. Defaults to None."""
    tag: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of tags to filter by. It must be the tag ID. Also matches parent tags. Defaults to an empty list."""
    dtag: t.Optional[t.List[str]] = field(default_factory=list)
    """A list of tags to filter by. It must be the tag ID. Does not match parent tags. Defaults to an empty list."""
    anime_id: t.Optional[int] = field(default_factory=int)
    """See :attr:`VN.anime_id`. An integer representing the AniDB ID of the VN. Defaults to 0."""
    
    # TODO: Label needs more thought put into it. There are countless ways to filter so it's hard
    # know what is a good way to do it or not.
    # label: t.Optional[t.List[Label]] = field(default_factory=list)
    """A list of labels to filter by. Defaults to an empty list."""

    def _dict(self) -> t.Dict[str, t.Any]:
        """Convert the VNFilter object to a dictionary."""
        initial_dict =  {
            "id": self.id if self.id else None,
            "lang": self.lang if self.lang else None,
            "olang": self.olang if self.olang else None,
            "platform": self.platform if self.platform else None,
            "released": self.released._parse() if self.released else None,
            "length": self.length._parse() if self.length else None,
            "tag": self.tag if self.tag else None,
            "dtag": self.dtag if self.dtag else None,
            "anime_id": self.anime_id,
            # "label": [l for l in self.label] if self.label else None,
        }
        return {k: v for k, v in initial_dict.items() if v}

    # TODO: Add support for the rest of the filters (release, character, staff, developer).
    # These all have their own filter objects, however, so it must be later.

# TODO: See above.
# @dataclass(slots=True)
# class Label:
#     """A label object as defined by the VNDB API. It is used to filter specific VNs, made by users."""
#     user_id: str
#     """The VNDB user ID of the user who created the label."""
#     label_id: str
#     """The VNDB ID of the label."""

@dataclass(slots=True, frozen=True)
class Released:
    """A nested filter object for the `released` attribute. Only one attribute can be set."""
    eq: t.Optional[str] = None
    neq: t.Optional[str] = None
    lt: t.Optional[str] = None
    gt: t.Optional[str] = None
    geq: t.Optional[str] = None
    leq: t.Optional[str] = None

    def __post_init__(self) -> None:
        sum_of_selected = sum([bool(self.eq), bool(self.neq), bool(self.lt), bool(self.gt), bool(self.geq), bool(self.leq)])
        if sum_of_selected > 1:
            raise IllformedVNDBQuery("From filter Released: Only one of the attributes can be set at a time.")
        elif sum_of_selected == 0:
            raise IllformedVNDBQuery("From filter Released: At least one of the attributes must be set.")

    def _parse(self) -> t.List[str] | None:
        if self.eq:
            return ["=", str(self.eq)]
        elif self.neq:
            return ["!=", str(self.neq)]
        elif self.lt:
            return ["<", str(self.lt)]
        elif self.gt:
            return [">", str(self.gt)]
        elif self.geq:
            return [">=", str(self.geq)]
        elif self.leq:
            return ["<=", str(self.leq)]
        return None
    


@dataclass(slots=True, frozen=True)
class Length:
    """See :attr:`VN.length`. A nested filter object for the `length` attribute. Only one attribute can be set."""
    eq: t.Optional[int] = None
    neq: t.Optional[int] = None

    def __post_init__(self) -> None:
        sum_of_selected = sum([bool(self.eq), bool(self.neq)])
        if sum_of_selected > 1:
            raise IllformedVNDBQuery("From filter Length: Only one of the attributes can be set at a time.")
        elif sum_of_selected == 0:
            raise IllformedVNDBQuery("From filter Length: At least one of the attributes must be set.")

    def _parse(self) -> t.List[str | int] | None:
        if self.eq:
            return ["=", int(self.eq)]
        elif self.neq:
            return ["!=", int(self.neq)]
        return None
            


@dataclass(slots=True, frozen=True)
class VN:
    id: int
    length: int
    """An integer representing the playtime estimate of the VN. It can contain a value between 1 (Very short) to 5 (Very long).
    If there are no votes on the VN's playtime, it will fall back to the entires' length field.
    """
    rating: int
    """An integer representing the VN's rating. It can have a value between 10 and 100."""
    votecount: int
    """An integer representing the number of votes on the VN's rating."""
    devstatus: int
    """An integer representing the VN's development status. It's values can be: 0 (Finished), 1 (In Development), or 2 (Cancelled)."""


class VNDBClient:
    """
    A client object for interacting with the [VNDB](https://vndb.org) API.

    ## Information

    ### Usage Terms

    API access is rate-limited to 200 requests per 5 minutes and up to 1 second of execute time per minute.
    Requests that exceed 3 seconds in length will be aborted.

    ## Database Querying

    The query format for a JSON object fetched using `POST` is as follows:
    ```
    {
        "filters": [],
        "fields": "",
        "sort": "id",
        "reverse": false,
        "results": 10,
        "page": 1,
        "user": null,
        "count": false,
        "compact_filters": false,
        "normalized_filters": false
    }
    ```
    Such fields also translate to this class, so you can use them as 
    keyword arguments in `POST` requests, not including the `filters` or `fields` 
    fields, as they are handles by the individual methods.

    ### Response format
    ```
    {
        "results": [],
        "more": false,
        "count": 1,
        "compact_filters": "",
        "normalized_filters": [],
    }
    ```
    
    ## Example usage

    ```
    async with VNDBClient() as client:
        stats = await client.get_stats()
        print(stats.vn) # Get number of VNs in VNDB.
    ```
    >>> 54366

    """

    ENDPOINT: t.Final = "https://api.vndb.org/kana"

    def __init__(self) -> None:
        self.session: t.Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "VNDBClient":
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type: t.Optional[BaseException], exc_value: t.Optional[BaseException], traceback: t.Optional[t.Any]) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    @property
    def _client(self) -> aiohttp.ClientSession:
        """Validation for the session."""
        if not self.session:
            raise RuntimeError(NOT_INITIALIZED)
        return self.session
    
    def _parse_vn_filter(self, filter: VNFilter | None) -> t.List[t.Any]:
        """
        Parse the VNFilter object into something that can actually be used by the VNDB API.
        """
        # Check if there is only one parameter set in the VNFilter object:
        if not filter: return []
        parsed_list: t.List[t.Any] = [
            "and",
        ]
        temp_list: t.List[t.Any] = []
        for k, v in filter._dict().items():
            if isinstance(v, list):
                if isinstance(v[0], str):
                    for value in v:
                        temp_list.append([k, "=", value])
                else:
                    temp_list.append([k] + v)
            if isinstance(v, str):
                temp_list.append([k, "=", v])
            if isinstance(v, int):
                print([k, "=", int(v)])
                temp_list.append([k, "=", int(v)])
        
        parsed_list = [parsed_list[0]] + temp_list
        return parsed_list
        

    async def get_schema(self) -> t.Dict[str, t.Any]:
        """
        Returns a JSON object with metadata about several API objects.
        """
        try:
            async with self._client.get(f"{self.ENDPOINT}/schema") as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to fetch schema: {response.status}")
                return await response.json()
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {e}")
    
    async def get_stats(self) -> VNDBStats:
        """
        Returns a few overall database statistics from the VNDB API.
        """
        try:
            async with self._client.get(f"{self.ENDPOINT}/stats") as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to fetch stats: {response.status}")
                data = await response.json()
                return VNDBStats(**data)
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {e}")
        
    async def get_user(self, q: str, *, default_only=False) -> VNDBUser | None:
        """
        Returns a user object from the VNDB API. 

        Args:
            q (str): The username or ID of the user to fetch.
            default_only (bool): If True, only fetches the default fields (id and username). Defaults to `True`.
        
        Returns:
            out (Union[VNDBUser, None]): A VNDBUser object if found, otherwise None.
        """
        URL = f"{self.ENDPOINT}/user?q={q}&fields=lengthvotes,lengthvotes_sum"
        if default_only:
            URL = f"{self.ENDPOINT}/user?q={q}"
        try:
            async with self._client.get(URL) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                if not data: return None
                return VNDBUser(**data[q])
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {e}")
        
    async def get_authinfo(self, token: str) -> VNDBAuthInfo | None:
        """
        Validates and returns information about the given [API token](https://api.vndb.org/kana#user-authentication).

        Args:
            token (str): The API token to validate.
        
        Returns:
            out (Union[VNDBAuthInfo, None]): Returns a VNDBAuthInfo object if found, otherwise None.
        """
        headers = {
            'Authorization': 'token ' + token,
        }
        try:
            async with self._client.get(f"{self.ENDPOINT}/authinfo", headers=headers) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                if not data: return None
                return VNDBAuthInfo(**data)
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {e}")
            
    # ---Database Querying---

    async def post_vn(self, query: str, *, filter: VNFilter | None = None) -> t.List[VN] | None:
        parsed_filter = ["search", "=", query]
        if filter:
            parsed_filter = self._parse_vn_filter(filter)
            parsed_filter.append(["search", "=", query])
        payload = {
            "filters": parsed_filter,
            "fields": "id,length,rating,devstatus,votecount",
        }
        async with self._client.post(f"{self.ENDPOINT}/vn", json=payload) as response:
            if response.status == 429:
                raise RuntimeError("Rate limit exceeded. Please wait a few seconds and try again.")
            elif response.status != 200:
                raise RuntimeError(f"Failed to fetch VN: {response}")
            data = await response.json()
            if not data: return None
            array_of_vn: t.List[VN] = []
            for entry in data["results"]:
                array_of_vn.append(VN(**entry))
            return array_of_vn
                
     
async def main() -> None:
    async with VNDBClient() as client:
        filter = VNFilter(
            tag=["g3998", "g7"] # Clinical Depression, Horror
        )
        vns = await client.post_vn("saya no uta", filter=filter)
        if vns:
            for vn in vns: print(vn.id)

if __name__ == "__main__":
    import platform
    if platform.system() == "Linux":
        uvloop.install()
    asyncio.run(main())