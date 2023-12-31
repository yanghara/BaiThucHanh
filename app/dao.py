from app.Models import Category, Product, User, Receipt, ReceiptDetails
import hashlib
from app import app, db
from flask_login import current_user
from sqlalchemy import func
import cloudinary.uploader

def load_categories():
    return Category.query.all()
    # return [{
    #     'id': 1,
    #     'name': 'Điện thoại'
    # }, {
    #     'id': 2,
    #     'name': 'Máy tính'
    # }, {
    #     'id': 3,
    #     'name': 'Apple Watch'
    # }]


def load_products(kw, cate_id, page=None):
    products = Product.query
    if kw:
        products = products.filter(Product.name.contains(kw))
    # produst = [{
    #     'id': 1,
    #     'name': 'Iphone 14 promax 1TB',
    #     'prices': '46.999.000',
    #     'image': 'https://th.bing.com/th/id/OIP.Zp2XttHJZY8GzCPKim2V4AHaHa?pid=ImgDet&rs=1'
    # }, {
    #     'id': 2,
    #     'name': 'Iphone 15 promax 512',
    #     'prices': '42.190.000',
    #     'image': 'https://cf.shopee.vn/file/1e1ed727b366712356405041c20c25ab'
    # }, {
    #     'id': 3,
    #     'name': 'SamSung Galaxy S20',
    #     'prices': '36.900.000',
    #     'image': 'https://cdn.shopify.com/s/files/1/1876/0973/products/samsungs20fE_530x@2x.jpg?v=1679352539'
    # }, {
    #     'id': 4,
    #     'name': 'SamSung G. S20+',
    #     'prices': '40.000.000',
    #     'image': 'https://www.theelectronicswarehouse.co.uk/wp-content/uploads/2020/09/s20-BTS-Edition-back.jpg'
    # }, {
    #     'id': 5,
    #     'name': 'Iphone 11 promax 1T',
    #     'prices': '26.999.000',
    #     'image': 'https://www.technocratng.com/wp-content/uploads/2021/01/Apple-iPhone-11-Pro-Max-select2-370x370.png'
    # }, {
    #     'id': 6,
    #     'name': 'LapTop HB 16GB Ram',
    #     'prices': '26.490.000',
    #     'image': 'https://th.bing.com/th/id/OIP.SxvtpGblnKO7qTXh3GP2EwHaFv?pid=ImgDet&rs=1'
    # }, {
    #     'id': 7,
    #     'name': 'Dell Inprison 15',
    #     'prices': '36.100.000',
    #     'image': 'https://www.bhphotovideo.com/images/images2000x2000'
    #              '/dell_i3567_3964blk_i3_7100u_8gb_2tb_windows_1399478.jpg'
    # }, {
    #     'id': 8,
    #     'name': 'Lenovo ThinkPad',
    #     'prices': '20.999.000',
    #     'image': 'https://www.bhphotovideo.com/images/images1500x1500/lenovo_20t6002mus_tp_e14_g2_ryzen_1595843.jpg'
    # }, {
    #     'id': 9,
    #     'name': 'MacBook Pro 15',
    #     'prices': '50.999.000',
    #     'image': 'https://i1.wp.com/laptopmedia.com/wp-content/uploads/2017/06/macbook_pro_13_a_1143_0_0.jpg?fit=2040'
    #              '%2C1727&ssl=1'
    # }, {
    #     'id': 10,
    #     'name': 'MacBook Air M1',
    #     'prices': '56.190.000',
    #     'image': 'https://th.bing.com/th/id/R.e87cff0dbddb57c93f5d48df87a1b6db?rik=YTSkq81ZkP914w&pid=ImgRaw&r=0'
    # }, {
    #     'id': 11,
    #     'name': 'Apple Watch S5',
    #     'prices': '16.999.000',
    #     'image': 'https://www.bhphotovideo.com/images/images2500x2500/apple_mwvf2ll_a_watch_5_gps_44mm_1506021.jpg'
    # }, {
    #     'id': 12,
    #     'name': 'Apple Watch SE',
    #     'prices': '10.100.000',
    #     'image': 'https://cdn.mos.cms.futurecdn.net/JpWwCZGm8zDDWkaGS7Nx9A-650-80.jpg'
    # }]
    #
    # if kw:
    #     produst = [x for x in produst if x['name'].find(kw) >= 0]
    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return products.slice(start, start + page_size)

    return products.all()


def product_count():
    return Product.query.count()


def get_user_by_id(user_id):
    return User.query.get(user_id)


# nó đều lấy cái khóa chính

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def app_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'], product_id=c['id'], receipt=receipt)
            db.session.add(d)

        db.session.commit()


def add_user(name, username, password, avatar):
    # import pdb
    # pdb.set_trace()
    # debuging fix
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password,
             avatar='https://cf.shopee.vn/file/1e1ed727b366712356405041c20c25ab')

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        u.avatar = res['secure_url']

    db.session.add(u)
    db.session.commit()


def count_productReceipt():
    return db.session.query(Category.id, Category.name,
                            func.count(Product.id)).join(Product, Product.category_id == Category.id, isouter=True).group_by(Category.id).all()


if __name__ == '__main__':
    with app.app_context():
        print(count_productReceipt())