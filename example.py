from avndb import VNDBClient, VNFilter
import asyncio

async def simple_example() -> None:
    async with VNDBClient() as client:
        vn_list = await client.post_vn("saya no uta")
        if vn_list:
            for vn in vn_list: print(f"ID {vn.id}: {vn.devstatus}")

async def with_filters() -> None:
    async with VNDBClient() as client:
        filter = VNFilter(
            tag=["g7"] # Horror
        )
        vn_list = await client.post_vn("saya no uta", filter=filter)
        if vn_list:
            for vn in vn_list: print(f"ID {vn.id}: {vn.devstatus}")

if __name__ == "__main__":
    asyncio.run(simple_example())
    print("--------")
    asyncio.run(with_filters())
    # Output:
    # ID v97: 0
    # ID v6742: 0
    # ID v22591: 2
    # ID v25119: 0
    # ID v26379: 0
    # --------
    # ID v97: 0
    # ID v22591: 2
