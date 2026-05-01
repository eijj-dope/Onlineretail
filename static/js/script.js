// ================= ADD TO CART =================
function addToCart(productId) {
    const qtyInput = document.getElementById(`qty-${productId}`);
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    fetch("/add_to_cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(res => res.json())
    .then(data => showToast(data.message))
    .catch(() => showToast("Something went wrong!"));
}

// ================= TOAST =================
function showToast(message) {
    let toast = document.getElementById("toast");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

// ================= INPUT LIMIT =================
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("input[type='number']").forEach(input => {
        input.addEventListener("input", () => {
            const max = parseInt(input.max);
            let value = parseInt(input.value);

            if (value > max) {
                input.value = max;
                showToast("Max stock reached!");
            }

            if (value < 1 || isNaN(value)) {
                input.value = 1;
            }
        });
    });
});