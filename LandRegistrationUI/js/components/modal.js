import { qs } from "../core/utils.js";

export function openModal({ title, body, footer = "" }) {
  const root = qs("#modalRoot");
  root.innerHTML = `
    <div class="modal-backdrop" role="dialog" aria-modal="true">
      <article class="modal">
        <header class="modal-header">
          <h2>${title}</h2>
          <button class="modal-close" type="button" aria-label="Close modal">x</button>
        </header>
        <div class="modal-body">${body}</div>
        ${footer ? `<footer class="modal-footer">${footer}</footer>` : ""}
      </article>
    </div>
  `;

  const close = () => {
    root.innerHTML = "";
    document.removeEventListener("keydown", onKeydown);
  };
  const onKeydown = (event) => {
    if (event.key === "Escape") close();
  };

  qs(".modal-close", root).addEventListener("click", close);
  qs(".modal-backdrop", root).addEventListener("click", (event) => {
    if (event.target.classList.contains("modal-backdrop")) close();
  });
  document.addEventListener("keydown", onKeydown);

  return { root, close };
}
