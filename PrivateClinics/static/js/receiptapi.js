function confirmPayment(receiptId) {
    if (confirm('Chắn chắn xác nhận hóa đơn đã thanh toán?')) {
        fetch(`/api/receipt/confirm/${receiptId}`,  {
            method: 'put',
            body: JSON.stringify({
                "receiptId": receiptId
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then((res) => res.json()).then((data) => {
            console.info(data)
            let s = document.getElementById('stat')
            s.innerText = data['status']

            let pd = document.getElementById('payDate')
            pd.innerText = data['payment_date']

            let a = document.getElementById('act')
            a.style.display = "none"
        })
    }
}