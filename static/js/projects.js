(() => {
  const endpointElement = document.getElementById("project-endpoints");
  const searchForm = document.getElementById("project-search-form");
  const searchInput = document.getElementById("search-input");
  const loadingState = document.getElementById("project-loading");
  const errorState = document.getElementById("project-error");
  const emptyState = document.getElementById("project-empty");
  const grid = document.getElementById("project-grid");
  const retryButton = document.getElementById("project-retry");

  if (!endpointElement || !searchForm || !searchInput || !loadingState || !errorState || !emptyState || !grid) {
    return;
  }

  const endpointData = endpointElement.dataset;
  const canEdit = JSON.parse(document.getElementById("project-can-edit").textContent);
  const isSuperuser = JSON.parse(document.getElementById("project-is-superuser").textContent);
  const isAuthenticated = JSON.parse(document.getElementById("project-is-authenticated").textContent);
  const csrfToken = document.getElementById("project-csrf-token").value;
  const idPlaceholder = "00000000-0000-0000-0000-000000000000";
  let activeController;

  function setState(state) {
    loadingState.classList.toggle("hide", state !== "loading");
    errorState.classList.toggle("hide", state !== "error");
    emptyState.classList.toggle("hide", state !== "empty");
    grid.classList.toggle("hide", state !== "grid");
  }

  function urlFor(template, projectId) {
    return template.replace(idPlaceholder, encodeURIComponent(projectId));
  }

  function formatStarCount(count) {
    return `${count} star${count === 1 ? "" : "s"}`;
  }

  function appendText(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    parent.append(element);
    return element;
  }

  function createPostForm(action, className, buttonText, buttonClass) {
    const form = document.createElement("form");
    form.method = "post";
    form.action = action;
    form.className = className;

    const csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrfmiddlewaretoken";
    csrfInput.value = csrfToken;
    form.append(csrfInput);

    const button = document.createElement("button");
    button.type = "submit";
    button.className = buttonClass;
    button.textContent = buttonText;
    form.append(button);
    return form;
  }

  function buildProjectCard(item) {
    const project = item.fields;
    const article = document.createElement("article");
    article.className = "experience-card project-card";

    if (project.project_image_url) {
      const image = document.createElement("img");
      image.className = "project-image";
      image.src = project.project_image_url;
      image.alt = `Gambar ${project.title}`;
      image.loading = "lazy";
      article.append(image);
    }

    appendText(article, "span", "experience-category", project.tech_stack);
    const heading = document.createElement("h2");
    const detailLink = document.createElement("a");
    detailLink.href = urlFor(endpointData.detailTemplate, item.pk);
    detailLink.textContent = project.title;
    heading.append(detailLink);
    article.append(heading);
    appendText(article, "p", "experience-description", project.description);

    const actions = document.createElement("div");
    actions.className = "project-card-actions project-actions";
    if (project.project_url) {
      const projectLink = document.createElement("a");
      projectLink.href = project.project_url;
      projectLink.target = "_blank";
      projectLink.rel = "noopener noreferrer";
      projectLink.className = "button";
      projectLink.textContent = "Lihat proyek";
      actions.append(projectLink);
    }

    if (isAuthenticated) {
      const starForm = createPostForm(
        urlFor(endpointData.starTemplate, item.pk),
        "star-form",
        project.is_starred ? "Unstar" : "Star",
        `button button-star${project.is_starred ? " is-starred" : ""}`,
      );
      const starButton = starForm.querySelector("button");
      starButton.setAttribute("aria-label", `${project.is_starred ? "Unstar" : "Star"} ${project.title}`);
      starButton.title = formatStarCount(project.star_count);
      appendText(starButton, "span", "star-count", formatStarCount(project.star_count));
      actions.append(starForm);
    } else {
      appendText(actions, "span", "star-count project-star-total", formatStarCount(project.star_count));
      const loginLink = document.createElement("a");
      loginLink.href = `${endpointData.loginUrl}?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;
      loginLink.textContent = "Login untuk memberi star";
      actions.append(loginLink);
    }

    if (canEdit) {
      const editLink = document.createElement("a");
      editLink.href = urlFor(endpointData.updateTemplate, item.pk);
      editLink.className = "button button-secondary";
      editLink.textContent = "Edit proyek";
      actions.append(editLink);
    }

    if (isSuperuser) {
      actions.append(createPostForm(
        urlFor(endpointData.deleteTemplate, item.pk),
        "project-delete-form",
        "Hapus proyek",
        "button button-secondary",
      ));
    }

    article.append(actions);
    return article;
  }

  async function fetchProjects(query = "") {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;
    setState("loading");

    const url = new URL(endpointData.jsonUrl, window.location.origin);
    if (query) url.searchParams.set("title", query);

    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Project request failed (${response.status})`);

      const projects = await response.json();
      if (controller.signal.aborted) return;
      grid.replaceChildren();

      if (projects.length === 0) {
        setState("empty");
        return;
      }

      const fragment = document.createDocumentFragment();
      projects.forEach((project) => fragment.append(buildProjectCard(project)));
      grid.append(fragment);
      setState("grid");
    } catch (error) {
      if (error.name === "AbortError") return;
      console.error("Gagal memuat proyek:", error);
      setState("error");
    }
  }

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = searchInput.value.trim();
    const url = new URL(window.location.href);
    if (query) url.searchParams.set("title", query);
    else url.searchParams.delete("title");
    window.history.replaceState({}, "", url);
    fetchProjects(query);
  });

  retryButton?.addEventListener("click", () => fetchProjects(searchInput.value.trim()));
  fetchProjects(searchInput.value.trim());
})();
