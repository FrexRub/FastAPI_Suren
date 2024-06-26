import asyncio

from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from core.models import db_helper, User, Profile, Post, Order, Product, OrderProductAssociation


async def create_user(session: AsyncSession, username: str) -> User:
    user: User = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    # result: Result = await session.execute(stmt)
    # user: User | None = result.scalars().one_or_none()
    user: User | None = await session.scalar(stmt)
    print(f"Find user by name {username}: {user}")
    return user


async def create_user_profile(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str = None
) -> Profile:
    profile: Profile = Profile(user_id=user_id, first_name=first_name, last_name=last_name)
    session.add(profile)
    await session.commit()
    return profile


async def show_user_with_profile(session: AsyncSession):
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    users = await session.scalars(stmt)
    for user in users:  # type: User
        print(user)
        print(user.profile.first_name)


async def create_posts(session: AsyncSession, user_id: int, *post_titles: str) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in post_titles]
    session.add_all(posts)
    await session.commit()
    for post in posts:
        print(post)
    return posts


async def get_user_with_post(session: AsyncSession):
    # Запрос один ко многим
    # В случае запроса через join возникает повторение пользователей пользователь - пост
    # чтобы пользователь был уникален используется параметр unique или другой способ запроса selectinload
    # для вариантов 1 и 2
    # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # для вариант 3
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)

    # users = await session.scalars(stmt) #1
    result: Result = await session.execute(stmt)  # 2, 3
    users = result.scalars()  # 3
    # users = result.unique().scalars() #2
    # for user in users.unique(): #1
    for user in users:
        print('**' * 10)
        print(user)
        for post in user.posts:
            print("-", post)


async def get_posts_with_author(session: AsyncSession):
    # Запрос многие к одному, повторение допустимо
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)
    for post in posts:
        print("post", post.title, "user", post.user.username)


async def get_user_with_post_profile(session: AsyncSession):
    stmt = select(User).options(
        selectinload(User.posts),  # один ко многим
        joinedload(User.profile),  # один к одному
    ).order_by(User.id)
    users = await session.scalars(stmt)

    for user in users:
        print('**' * 10)
        # проверяем наличие профиля у пользователя выводим его имя
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            print("-", post)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .options(
            # сквозная связка таблиц Профиль Пользователь Посты
            joinedload(Profile.user).selectinload(User.posts),
        )
        .order_by(Profile.id)
    )
    # stmt = (
    #     select(Profile)
    #     .join(Profile.user) # для сортировки по пользователю
    #     .options(
    #         joinedload(Profile.user).selectinload(User.posts),
    #     )
    #     .where(User.username == "john")
    #     .order_by(Profile.id)
    # )

    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def main_to_relations(session: AsyncSession):
    # await create_user(session=session, username="Sam")
    user_john = await get_user_by_username(session, "John")
    user_sam = await get_user_by_username(session, "Sam")
    # await create_user_profile(
    #     session=session,
    #     user_id=user_john.id,
    #     first_name="John"
    # )
    # await create_user_profile(
    #     session=session,
    #     user_id=user_sam.id,
    #     first_name="Sam",
    #     last_name="White"
    # )
    await show_user_with_profile(session=session)
    # await create_posts(
    #     session,
    #     user_john.id,
    #     "SQL 2.0",
    #     "SQLA Joins"
    # )
    # await create_posts(
    #     session,
    #     user_sam.id,
    #     "FastAPI intro",
    #     "FastAPI Advanse",
    #     "FastAPI more"
    # )
    # await get_user_with_post(session=session)
    # await get_posts_with_author(session=session)
    # await get_user_with_post_profile(session=session)
    await get_profiles_with_users_and_users_with_posts(session=session)


async def create_order(session: AsyncSession, promocode: str | None = None) -> Order:
    order: Order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
        session: AsyncSession,
        name: str,
        description: str,
        price: int,
) -> Product:
    product: Product = Product(name=name, description=description, price=price)
    session.add(product)
    await session.commit()
    return product


async def create_order_and_product(session: AsyncSession):
    order_one: Order = await create_order(session)
    order_promo: Order = await create_order(session, promocode="promo")

    mouse: Product = await create_product(
        session,
        name="Mouse",
        description="Great gaming mouse",
        price=123,
    )
    keyboard: Product = await create_product(
        session,
        name="Keyboard",
        description="Great gaming keyboard",
        price=149,
    )
    display: Product = await create_product(
        session,
        name="Display",
        description="Office display",
        price=299,
    )

    # Для добавления продуктов к ордеру необходимо подгрузить связи
    order_one = await session.scalar(
        select(Order).where(Order.id == order_one.id).
        options(
            selectinload(Order.products),
        )
    )

    order_promo = await session.scalar(
        select(Order).where(Order.id == order_promo.id).
        options(
            selectinload(Order.products),
        )
    )

    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(keyboard)
    # order_promo.products.append(display)
    order_promo.products = [keyboard, display]

    await session.commit()


# async def get_orders_with_products(session: AsyncSession) -> list[Order]:
#     stmt = select(Order).options(selectinload(Order.products)).order_by(Order.id)
#     orders = await session.scalars(stmt)
#     return list(orders)


async def get_orders_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = select(Order).options(
        selectinload(Order.products_details).joinedload(OrderProductAssociation.product)
    ).order_by(Order.id)
    orders = await session.scalars(stmt)
    return list(orders)


async def demo_m2m(session: AsyncSession):
    # await create_order_and_product(session)

    # запрос с использованием сквозной связки таблиц через secondary=order_product_association_table
    # orders: list[Order] = await get_orders_with_products(session)
    # for order in orders:
    #     print(order.id, order.promocode, order.created_at, "products:")
    #     for product in order.products:  # type: Product
    #         print("-", product.id, product.name, product.price)

    orders: list[Order] = await get_orders_with_products_assoc(session)
    gift_product = await create_product(
        session=session,
        name="Gift",
        description="Gift for yuo",
        price=0,
    )

    # каждому ордеру добавляем товар-подарок
    for order in orders:  # type: Order
        order.products_details.append(
            OrderProductAssociation(
                count=1,
                unit_price=0,
                product=gift_product,
            )
        )
    await session.commit()

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for order_product_details in order.products_details:  # type: OrderProductAssociation
            print("-", order_product_details.product.name, order_product_details.product.price,
                  "qty:", order_product_details.count)


async def main():
    async with db_helper.session_factory() as session:
        # await main_to_relations(session=session)
        await demo_m2m(session=session)


if __name__ == "__main__":
    asyncio.run(main())
