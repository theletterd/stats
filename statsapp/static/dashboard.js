// Renders the dashboard from /data. Some sources are slow external APIs, so the
// page shell (with a loading skeleton) is served first and the stats fill in after.

(function () {
    const container = document.getElementById("stats");
    const errorLine = document.getElementById("source-errors");

    // text longer than this reads better on a full-width card (e.g. book titles)
    const WIDE_TEXT_LENGTH = 24;

    let noteCount = 0;

    function el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function renderValue(value) {
        if (Array.isArray(value)) {
            if (value.length === 0) {
                return el("div", "card__value card__empty", "None yet");
            }
            const list = el("ul", "card__value card__list");
            value.forEach(item => list.appendChild(el("li", null, item)));
            return list;
        }
        return el("div", "card__value", String(value));
    }

    function renderNote(card, notes) {
        const id = "note-" + noteCount++;
        const button = el("button", "card__note", "i");
        button.type = "button";
        button.setAttribute("popovertarget", id);
        button.setAttribute("aria-label", "About this stat");
        button.title = notes;

        const popover = el("div", "note-popover", notes);
        popover.id = id;
        popover.setAttribute("popover", "");

        card.append(button, popover);
    }

    function renderStat(stat) {
        const value = stat.value;
        const isWide = Array.isArray(value) || String(value).length > WIDE_TEXT_LENGTH;

        const card = el("div", isWide ? "card card--wide" : "card");
        card.append(el("div", "card__label", stat.description), renderValue(value));

        if (stat.notes && stat.notes.trim()) {
            renderNote(card, stat.notes.trim());
        }
        return card;
    }

    function renderGroup(group) {
        const section = el("section", "stat-group");
        section.id = group.stat_group;
        if (group.description) {
            section.appendChild(el("h2", null, group.description));
        }
        group.stats.forEach(row => {
            const rowEl = el("div", "stat-row");
            row.forEach(stat => rowEl.appendChild(renderStat(stat)));
            section.appendChild(rowEl);
        });
        return section;
    }

    function render(data) {
        container.replaceChildren(...data.stats.map(renderGroup));

        if (data.stats.length === 0) {
            container.appendChild(el("p", "empty-state", "No stats to show right now."));
        }

        if (data.error_messages && data.error_messages.length) {
            errorLine.textContent = "Couldn't load: " + data.error_messages.join(", ");
            errorLine.hidden = false;
        }
    }

    fetch(container.dataset.src)
        .then(response => {
            if (!response.ok) throw new Error(response.status);
            return response.json();
        })
        .then(render)
        .catch(() => {
            container.replaceChildren(el("p", "empty-state", "Couldn't load stats. Try refreshing."));
        })
        .finally(() => container.removeAttribute("aria-busy"));
})();
