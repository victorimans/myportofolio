(() => {
  const endpoints = document.getElementById("blog-endpoints");
  const list = document.getElementById("blog-list");
  if (!endpoints || !list) return;

  const loadingState = document.getElementById("blog-loading");
  const errorState = document.getElementById("blog-error");
  const emptyState = document.getElementById("blog-empty");
  const canEdit = JSON.parse(document.getElementById("blog-can-edit").textContent);
  const isSuperuser = JSON.parse(document.getElementById("blog-is-superuser").textContent);
  const isAuthenticated = JSON.parse(document.getElementById("blog-is-authenticated").textContent);
  const csrfToken = endpoints.querySelector('[name="csrfmiddlewaretoken"]').value;
  const data = endpoints.dataset;
  let activeController;

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
    element.textContent = text;
    parent.append(element);
    return element;
  }

  function urlFor(template, id) {
    return template.replace("/0/", `/${encodeURIComponent(id)}/`);
  }

  function postForm(action, className, label, buttonClass, ariaLabel) {
    const form = document.createElement("form");
    form.method = "post";
    form.action = action;
    form.className = className;
    const token = document.createElement("input");
    token.type = "hidden";
    token.name = "csrfmiddlewaretoken";
    token.value = csrfToken;
    form.append(token);
    const button = appendText(form, "button", buttonClass, label);
    button.type = "submit";
    button.setAttribute("aria-label", ariaLabel);
    return form;
  }

  function buildCard(item) {
    const post = item.fields;
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
    appendText(metadata, "p", "blog-post-category", post.category_display);
    const actions = appendText(header, "div", "blog-post-actions", "");
    if (canEdit) {
      const edit = appendText(actions, "a", "button button-small", "Edit Blog");
      edit.href = urlFor(data.updateTemplate, item.pk);
      edit.setAttribute("aria-label", `Edit blog: ${post.title}`);
    }
    if (isSuperuser) {
      actions.append(postForm(
        urlFor(data.deleteTemplate, item.pk), "", "Hapus Blog",
        "button button-secondary button-small", `Delete blog: ${post.title}`,
      ));
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
      const form = postForm(
        urlFor(data.starTemplate, item.pk), "star-form", label,
        `button button-star${post.is_starred ? " is-starred" : ""}`, `${label} ${post.title}`,
      );
      const button = form.querySelector("button");
      button.title = post.star_count ? count : "Jadilah yang pertama memberi star";
      appendText(button, "span", "star-count", count);
      stars.append(form);
    } else {
      appendText(stars, "span", "star-count project-star-total", count);
      const login = appendText(stars, "a", "", "Login to star");
      login.href = `${data.loginUrl}?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
    }
    return article;
  }

  async function fetchBlog() {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;
    setState("loading");
    try {
      const response = await fetch(data.jsonUrl, {
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

  document.getElementById("blog-retry").addEventListener("click", fetchBlog);
  fetchBlog();
})();
