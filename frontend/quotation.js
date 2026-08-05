const API_URL = "http://127.0.0.1:5000/api/quotations";

document.addEventListener("DOMContentLoaded", () => {
    loadQuotations();
});

// Load quotations
async function loadQuotations() {

    const token = localStorage.getItem("access_token");

    try {

        const response = await fetch(API_URL, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            throw new Error("Failed to load quotations");
        }

        const quotations = await response.json();

        const table = document.getElementById("quotationTable");
        table.innerHTML = "";

        quotations.forEach(q => {

            let statusClass = "status-pending";

            if (q.status === "Accepted") {
                statusClass = "status-accepted";
            }

            if (q.status === "Rejected") {
                statusClass = "status-rejected";
            }

            table.innerHTML += `
                <tr>
                    <td>${q.id}</td>
                    <td>${q.product_name}</td>
                    <td>${q.customer_name}</td>
                    <td>${q.quantity}</td>
                    <td>₹${q.offered_price}</td>

                    <td class="${statusClass}">
                        ${q.status}
                    </td>

                    <td>
                        <button
                            class="accept-btn"
                            onclick="updateQuotation(${q.id}, 'Accepted')">
                            Accept
                        </button>

                        <button
                            class="reject-btn"
                            onclick="updateQuotation(${q.id}, 'Rejected')">
                            Reject
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (error) {

        console.error(error);
        alert("Unable to load quotations.");

    }
}

// Update quotation
async function updateQuotation(id, status) {

    const token = localStorage.getItem("access_token");

    try {

        const response = await fetch(`${API_URL}/${id}`, {

            method: "PUT",

            headers: {

                "Content-Type": "application/json",

                "Authorization": "Bearer " + token

            },

            body: JSON.stringify({

                status: status

            })

        });

        if (response.ok) {

            alert("Quotation Updated Successfully");
            loadQuotations();

        } else {

            alert("Unable to Update Quotation");

        }

    } catch (error) {

        console.error(error);

    }

}