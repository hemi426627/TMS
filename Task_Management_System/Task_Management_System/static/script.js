function GetResponse(url, params = {}, callback = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;

    fetch(fullUrl, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }).then(res => res.json())
        .then(result => {
            if (result.success) {
                callback.onSuccess && callback.onSuccess(result);
            }
            else {
                callback.onError && callback.onError(result);
            }
        })
        .catch(err => {
            callback.onError && callback.onError({
                success: false,
                message: err.message,
                data: []
            });
        });
}

function initDynamicTable(tableId, data = [], options = {
    responsive: true,
    paging: true,
    searching: true,
    ordering: true,
    pageLength: 5,
    lengthMenu: [5, 10, 25, 50],
    language: {
        search: "_INPUT_",
        searchPlaceholder: "Search table..."
    }
}) {
    if (data != []) {
        var tableBody = document.querySelector(`${tableId} tbody`);
        if (!tableBody) return;

        // Clear table body
        tableBody.innerHTML = '';

        // Add rows dynamically if data is provided
        data.forEach((row, index) => {
            var tr = document.createElement('tr');
            var rowHtml = Object.values(row).map(val => `<td>${val}</td>`).join('');
            tr.innerHTML = rowHtml;
            tableBody.appendChild(tr);
        });
    }

    // Destroy existing DataTable if exists
    if ($.fn.DataTable.isDataTable(tableId)) {
        $(tableId).DataTable().destroy();
    }

    // Initialize DataTable
    $(tableId).DataTable(options);
}