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