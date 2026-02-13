function dynamicResponse(url, params = {}, callback = {}, method = "GET") {
    method = method.toUpperCase();
    let fullUrl = url;

    if (method === "GET" && Object.keys(params).length > 0) {
        const queryString = new URLSearchParams(params).toString();
        fullUrl = `${url}?${queryString}`;
    }

    const options = {
        method: method,
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    };

    if (method !== "GET" && Object.keys(params).length > 0) {
        options.body = JSON.stringify(params);
    }

    fetch(fullUrl, options)
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                callback.onSuccess && callback.onSuccess(result);
            } else {
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

function dynamicTabs({
    tabsSelector = '#appTabs .nav-link',
    panesSelector = '#tabContent .tab-pane',
    defaultTab = null,
    activeClass = 'active'
} = {}) {

    const tabs = document.querySelectorAll(tabsSelector);
    const panes = document.querySelectorAll(panesSelector);

    if (!tabs.length || !panes.length) return;

    function setActiveTab(tabName, updateHash = true) {
        tabs.forEach(tab =>
            tab.classList.toggle(activeClass, tab.dataset.tab === tabName)
        );

        panes.forEach(pane =>
            pane.classList.toggle(activeClass, pane.id === tabName)
        );

        // Auto call function if defined
        const activeTab = [...tabs].find(t => t.dataset.tab === tabName);
        const loadFn = activeTab?.dataset.load;

        if (loadFn && typeof window[loadFn] === 'function') {
            window[loadFn]();
        }

        if (updateHash) {
            history.replaceState(null, null, `#${tabName}`);
        }
    }

    // Initial tab
    const hashTab = window.location.hash.replace('#', '');
    const firstTab = defaultTab || tabs[0]?.dataset.tab;
    const initialTab = hashTab || firstTab;

    setActiveTab(initialTab, false);

    // Click handling
    tabs.forEach(tab => {
        tab.addEventListener('click', e => {
            e.preventDefault();
            setActiveTab(tab.dataset.tab);
        });
    });

    // Optional: listen to browser back/forward
    window.addEventListener('hashchange', () => {
        const tabName = window.location.hash.replace('#', '');
        if (tabName) setActiveTab(tabName, false);
    });
}

function dynamicTable({
    tableId,
    html = undefined,
    data = [],
    buttonText = null,
    buttonOnClick = null,
    paging = true,
    pageLength = 30,
    lengthMenu = [5, 10, 25, 50, 100],
    searching = true,
    ordering = true,
    autoWidth = false
}) {
    const tableSelector = `#${tableId}`;
    const $table = $(tableSelector);

    /* Destroy old DataTable FIRST */
    if ($.fn.DataTable.isDataTable(tableSelector)) {
        $table.DataTable().clear().destroy();
    }

    var $tbody = $table.find("tbody");

    /* Append rows */
    if (html != undefined) {
        $tbody.empty().append(html);
    }
    else if (Array.isArray(data) && data.length > 0) {
        let dataHtml = "";
        data.forEach(row => {
            dataHtml += "<tr>";
            dataHtml += Object.values(row).map(v => `<td>${v ?? ""}</td>`).join("");
            dataHtml += "</tr>";
        });
        $tbody.empty().append(dataHtml);
    }
    else {
        $tbody.empty();
    }

    /* Init DataTable */
    $table.DataTable({
        paging,
        pageLength,
        lengthMenu,
        searching,
        ordering,
        autoWidth,
        dom: `<'row mb-2' <'col-md-6 d-flex align-items-center'f> <'col-md-6 d-flex justify-content-end table-actions'> > <'row' <'col-12'tr> > <'row mt-2 d-flex justify-content-between align-items-center' <'col-auto'l> <'col-auto'i>  <'col-auto'p> >`,
        language: {
            search: "",
            searchPlaceholder: "Search records...",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
        },
        initComplete: function () {
            if (buttonText && buttonOnClick) {
                $(`${tableSelector}_wrapper .table-actions`).html(`
                    <button class="btn btn-primary btn-sm" onclick="${buttonOnClick}">
                        ${buttonText}
                    </button>
                `);
            }
        }
    });
}

function dynamicModal({ title, content, contentAction = undefined, btnAddEditText = undefined, addEditOnClick = undefined, modalWidth = 40 }) {
    const $modal = $("#dynamicModal");
    const $modalDialog = $modal.find(".modal-dialog");
    const $modalTitle = $("#modal-title");
    const $btnAddEdit = $("#btnAddEdit");

    // Set modal title
    $modalTitle.text(title);

    // Set or hide Add/Edit button
    if (btnAddEditText !== undefined) {
        $btnAddEdit.text(btnAddEditText).show();
    } else {
        $btnAddEdit.hide();
    }

    // Set modal content
    $modal.find(".modal-body").empty().append(content);

    // Execute optional content action
    if (typeof contentAction === "function") {
        contentAction();
    }

    // Set custom width
    $modalDialog.css("max-width", modalWidth + "%");

    // Show the modal
    const modal = new bootstrap.Modal($modal[0]);
    modal.show();

    // Attach Add/Edit click handler if provided
    if (typeof addEditOnClick === "function") {
        $btnAddEdit.off("click").on("click", function () {
            const shouldClose = addEditOnClick();
            if (shouldClose !== false) {
                modal.hide();
            }
        });
    }
}

function initSelect2InDynamicModal(selectSelector, options = {}) {

    const modal = $('#dynamicModal');
    const $select = modal.find(selectSelector);

    // Guard: element not found
    if (!$select.length) return;

    // Guard: already initialized
    if ($select.hasClass('select2-hidden-accessible')) return;

    $select.select2({
        placeholder: "Search",
        allowClear: true,
        width: '100%',
        dropdownParent: modal,
        ...options
    });
}

const CKEditors = {}; // store editor instances globally

function initCKEditor(selector, config = {}) {
    const el = document.querySelector(selector);
    if (!el) return Promise.reject('Element not found');

    // destroy old instance if exists
    if (CKEditors[selector]) {
        CKEditors[selector].destroy();
        CKEditors[selector] = null;
    }

    return ClassicEditor
        .create(el, config)
        .then(editor => {
            CKEditors[selector] = editor;
            return editor;
        })
        .catch(error => console.error(error));
}

function getCKEditorData(selector) {
    return CKEditors[selector] ? CKEditors[selector].getData() : '';
}

function destroyCKEditor(selector) {
    if (CKEditors[selector]) {
        CKEditors[selector].destroy();
        CKEditors[selector] = null;
    }
}