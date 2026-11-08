(() => {
  const endpoints = document.getElementById("blog-endpoints");
  const list = document.getElementById("blog-list");
  const searchForm = document.getElementById("blog-search-form");
  const searchInput = document.getElementById("blog-search-input");
  const blogForm = document.getElementById("blog-form");
  const SEARCH_DEBOUNCE_DELAY = 300;
  if (!endpoints || !list || !searchForm || !searchInput) return;

  const loadingState = document.getElementById("blog-loading");
  const errorState = document.getElementById("blog-error");
  const emptyState = document.getElementById("blog-empty");
  const canEdit = JSON.parse(document.getElementById("blog-can-edit").textContent);
  const isSuperuser = JSON.parse(document.getElementById("blog-is-superuser").textContent);
  const isAuthenticated = JSON.parse(document.getElementById("blog-is-authenticated").textContent);
  const csrfToken = endpoints.querySelector('[name="csrfmiddlewaretoken"]').value;
  const data = endpoints.dataset;
  const formModal = document.getElementById("blog-form-modal");
  const formTitle = document.getElementById("blog-form-modal-title");
  const submitButton = blogForm?.querySelector('button[type="submit"]');
  const categoryLabels = {
    ai: "AI",
    dsa: "DSA",
    "web-development": "Web Development",
    career: "Career",
    personal: "Personal",
  };
  let activeController;
  let searchDebounceTimer;
  let editingId = null;

  function setState(state) {
    loadingState.classList.toggle("hide", state !== "loading");
    errorState.classList.toggle("hide", state !== "error");
    emptyState.classList.toggle("hide", state !== "empty");
    list.classList.toggle("hide", state !== "list");
    list.setAttribute("aria-busy", String(state === "loading"));
  }

  function appendText(parent, tag, className, text) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = text ?? "";
    parent.append(element);
    return element;
  }

  function urlFor(template, id) {
    return template.replace("/0/", `/${encodeURIComponent(id)}/`);
  }

  function blogErrorMessage(result, status) {
    const messages = [];
    function collect(value, field = "") {
      if (Array.isArray(value)) {
        value.forEach((item) => collect(item, field));
      } else if (value && typeof value === "object") {
        Object.entries(value).forEach(([key, nested]) => collect(nested, key === "detail" ? "" : key));
      } else if (typeof value === "string") {
        messages.push(field ? `${field}: ${value}` : value);
      }
    }
    collect(result);
    return messages.join(" ") || `Permintaan gagal (HTTP ${status}).`;
  }

  async function writeBlog(url, method, payload) {
    const options = {
      method,
      headers: {
        Accept: "application/json",
        "X-CSRFToken": csrfToken,
      },
    };
    if (payload !== undefined) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload);
    }
    const response = await fetch(url, options);
    if (response.status === 204) return null;
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(blogErrorMessage(result, response.status));
    return result;
  }

  function createActionButton(parent, label, className, ariaLabel) {
    const button = appendText(parent, "button", className, label);
    button.type = "button";
    if (ariaLabel) button.setAttribute("aria-label", ariaLabel);
    return button;
  }

  function buildCard(post) {
    const article = document.createElement("article");
    article.className = "blog-post";
    if (post.picture_link) {
      const image = document.createElement("img");
      image.className = "blog-post-image";
      image.src = post.picture_link;
      image.alt = `Gambar ${post.title}`;
      image.loading = "lazy";
      article.append(image);
    }

    const header = appendText(article, "div", "blog-post-header", "");
    const metadata = appendText(header, "div", "", "");
    appendText(metadata, "p", "blog-post-date", new Date(post.created_at).toLocaleDateString("en-GB", {
      day: "numeric", month: "long", year: "numeric",
    }));
    appendText(metadata, "p", "blog-post-category", categoryLabels[post.category] || post.category);
    const actions = appendText(header, "div", "blog-post-actions", "");

    if (canEdit) {
      const edit = createActionButton(actions, "Edit Blog", "button button-small", `Edit blog: ${post.title}`);
      edit.dataset.action = "edit";
      edit.dataset.id = post.id;
    }
    if (isSuperuser) {
      const remove = createActionButton(actions, "Hapus Blog", "button button-secondary button-small", `Hapus blog: ${post.title}`);
      remove.dataset.action = "delete";
      remove.dataset.id = post.id;
    }

    appendText(article, "h2", "", post.title);
    const content = appendText(article, "div", "blog-post-content", "");
    post.content.replace(/\r\n?/g, "\n").split(/\n{2,}/).forEach((paragraph) => {
      const element = appendText(content, "p", "", "");
      paragraph.split("\n").forEach((line, index) => {
        if (index) element.append(document.createElement("br"));
        element.append(document.createTextNode(line));
      });
    });

    const stars = appendText(article, "div", "blog-post-star", "");
    const count = `${post.star_count} star${post.star_count === 1 ? "" : "s"}`;
    if (isAuthenticated) {
      const label = post.is_starred ? "Unstar" : "Star";
      const button = createActionButton(
        stars, label, `button button-star${post.is_starred ? " is-starred" : ""}`, `${label} ${post.title}`,
      );
      button.dataset.action = "star";
      button.dataset.id = post.id;
      button.title = post.star_count ? count : "Jadilah yang pertama memberi star";
      appendText(button, "span", "star-count", count);
    } else {
      appendText(stars, "span", "star-count project-star-total", count);
      const login = appendText(stars, "a", "", "Login to star");
      login.href = `${data.loginUrl}?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
    }
    return article;
  }

  async function fetchBlog(query = "") {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;
    setState("loading");
    const url = new URL(data.jsonUrl, window.location.origin);
    if (query) url.searchParams.set("title", query);
    emptyState.textContent = query ? "Tidak ada blog yang cocok dengan pencarian." : "Belum ada blog yang ditambahkan.";
    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Blog request failed (${response.status})`);
      const posts = await response.json();
      if (controller.signal.aborted) return;
      if (!Array.isArray(posts)) throw new Error("Invalid Blog response");
      const fragment = document.createDocumentFragment();
      posts.forEach((post) => fragment.append(buildCard(post)));
      list.replaceChildren(fragment);
      setState(posts.length ? "list" : "empty");
    } catch (error) {
      if (controller.signal.aborted) return;
      setState("error");
    }
  }

  function formPayload() {
    const fields = new FormData(blogForm);
    return Object.fromEntries(["title", "content", "category", "picture_link"].map((name) => [name, fields.get(name)]));
  }

  async function saveBlog(event) {
    event.preventDefault();
    if (submitButton.disabled) return;
    submitButton.disabled = true;
    try {
      const url = editingId ? urlFor(data.detailTemplate, editingId) : data.jsonUrl;
      await writeBlog(url, editingId ? "PATCH" : "POST", formPayload());
      formModal.hidePopover();
      showToast("Berhasil", editingId ? "Blog berhasil diperbarui." : "Blog berhasil ditambahkan.", "success");
      blogForm.reset();
      editingId = null;
      await fetchBlog(searchInput.value.trim());
    } catch (error) {
      showToast("Gagal menyimpan blog", error.message, "error");
    } finally {
      submitButton.disabled = false;
    }
  }

  async function editBlog(id) {
    try {
      const response = await fetch(urlFor(data.detailTemplate, id), { headers: { Accept: "application/json" } });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(blogErrorMessage(result, response.status));
      blogForm.elements.namedItem("title").value = result.title;
      blogForm.elements.namedItem("content").value = result.content;
      blogForm.elements.namedItem("category").value = result.category;
      blogForm.elements.namedItem("picture_link").value = result.picture_link || "";
      editingId = result.id;
      formTitle.textContent = "Edit Blog";
      submitButton.textContent = "Simpan Perubahan";
      formModal.showPopover();
    } catch (error) {
      showToast("Gagal membuka blog", error.message, "error");
    }
  }

  async function handleAction(event) {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;
    const action = button.dataset.action;
    const id = button.dataset.id;
    if (action === "edit") {
      await editBlog(id);
      return;
    }
    if (action === "delete" && !window.confirm("Hapus blog ini?")) return;
    button.disabled = true;
    try {
      if (action === "star") {
        await writeBlog(urlFor(data.starTemplate, id), "POST");
        showToast("Berhasil", "Star blog diperbarui.", "success");
      } else {
        await writeBlog(urlFor(data.detailTemplate, id), "DELETE");
        showToast("Berhasil", "Blog berhasil dihapus.", "success");
      }
      await fetchBlog(searchInput.value.trim());
    } catch (error) {
      showToast("Permintaan gagal", error.message, "error");
    } finally {
      button.disabled = false;
    }
  }

  function resetFormModal() {
    if (!blogForm) return;
    blogForm.reset();
    editingId = null;
    formTitle.textContent = isSuperuser ? "Tambah Blog Baru" : "Edit Blog";
    submitButton.textContent = isSuperuser ? "Tambah Blog" : "Simpan Perubahan";
  }

  function searchBlog() {
    const query = searchInput.value.trim();
    const url = new URL(window.location.href);
    if (query) url.searchParams.set("title", query);
    else url.searchParams.delete("title");
    window.history.replaceState({}, "", url);
    fetchBlog(query);
  }

  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchDebounceTimer);
    activeController?.abort();
    searchDebounceTimer = window.setTimeout(searchBlog, SEARCH_DEBOUNCE_DELAY);
  });
  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    window.clearTimeout(searchDebounceTimer);
    searchBlog();
  });
  document.getElementById("blog-retry").addEventListener("click", () => {
    window.clearTimeout(searchDebounceTimer);
    searchBlog();
  });
  blogForm?.addEventListener("submit", saveBlog);
  list.addEventListener("click", handleAction);
  formModal?.addEventListener("toggle", (event) => {
    if (!event.newState || event.newState === "closed") resetFormModal();
  });
  fetchBlog(searchInput.value.trim());
})();
