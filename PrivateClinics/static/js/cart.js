function updateCart(data) {
    let d = document.getElementsByClassName('cart-counter')
    for (let i = 0; i < d.length; i++)
        d[i].innerText = data.total_quantity
}

function addToCart(id, name, unit) {
    fetch('/api/cart', {
        method: 'POST',
        body:JSON.stringify({
            "id": id,
            "name": name,
            "unit": unit
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then((data) => {
        console.info(data)
        updateCart(data)
    })
}

function updateQuantity(id, obj) {
    fetch(`/api/cart/uQ${id}`, {
        method: "put",
        body: JSON.stringify({
            "quantity": obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then((res) => res.json()).then((data) => {
        console.info(data)
        updateCart(data)
    })
}

function updateUsage(id, obj) {
    fetch(`/api/cart/uU${id}`, {
        method: "put",
        body: JSON.stringify({
            "usage": obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then((res) => res.json()).then((data) => {
        console.info(data)
    })
}

function deleteCartItem(id) {
    if (confirm("Bạn có chắc chắn muốn xóa thuốc này?")) {
        fetch(`/api/cart/del${id}`, {
            method:'delete'
        }).then((res) => res.json()).then((data) => {
            console.info(data)
            updateCart(data)

            let r = document.getElementById(`${id}`)
            r.style.display = "none"
        })
    }
}