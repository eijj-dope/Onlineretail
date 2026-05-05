// ================= ADD TO CART =================
function addToCart(productId) {
    const qtyInput = document.getElementById(`qty-${productId}`);
    const qty = qtyInput && qtyInput.value ? parseInt(qtyInput.value) : 1;

    fetch("/add_to_cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: qty
        })
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message); // use alert first (for testing)
    })
    .catch(err => console.error(err));
}

function showToast(message, type = "success") {
    let toast = document.getElementById("toast");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.className = "toast-box"; // IMPORTANT
        document.body.appendChild(toast);
    }

    toast.textContent = message;

    // reset + apply styles
    toast.className = "toast-box show";

    if (type === "error") {
        toast.classList.add("toast-error");
    }

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