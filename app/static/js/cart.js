function addToCart(id, name, price){
    fetch('api/cart', {
        method: 'post',
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            'Content-Type': 'application/json; charset=utf8'
        }
    }).then(function(res){
        return res.json();
    }).then(function(data){
        let items = document.getElementsByClassName('counter_cart')
        for (let item of items)
            item.innerText = data.total_quantity;
    });
}