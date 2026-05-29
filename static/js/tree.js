/**
 * EV House Family Tree - D3.js Interactive Visualization
 */

// --- Constants ---
const NODE_WIDTH = 180;
const NODE_HEIGHT = 60;
const DURATION = 500;

// State
let selectedNodeId = null;

// --- Color helpers ---
const genderColors = {
    Male: "#3498db",
    Female: "#e91e63",
};

function nodeColor(d) {
    return genderColors[d.data.gender] || "#95a5a6";
}

function vitalBadge(d) {
    if (d.data.vital_stats && d.data.vital_stats.toLowerCase().includes("late")) {
        return " ⚰";
    }
    return "";
}

// --- Build SVG ---
const svg = d3.select("#tree-svg");
const width = () => document.getElementById("tree-container").clientWidth;
const height = () => document.getElementById("tree-container").clientHeight;

svg.attr("width", width()).attr("height", height());

// Zoom behavior
const g = svg.append("g");

const zoom = d3.zoom()
    .scaleExtent([0.1, 3])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
    });

svg.call(zoom);

// Add zoom controls
const zoomContainer = d3.select("#tree-container")
    .append("div")
    .attr("class", "zoom-controls");

zoomContainer.append("button")
    .html("+")
    .on("click", () => svg.transition().duration(300).call(zoom.scaleBy, 1.3));

zoomContainer.append("button")
    .html("−")
    .on("click", () => svg.transition().duration(300).call(zoom.scaleBy, 0.7));

// --- Tree layout ---
const treeLayout = d3.tree()
    .size([width() - 40, height() - 120])
    .separation((a, b) => (a.parent === b.parent ? 1.2 : 1.6));

let root;

// --- Fetch and render ---
async function init() {
    const data = await d3.json("/api/tree");
    root = d3.hierarchy(data);
    root.x0 = width() / 2;
    root.y0 = 80;

    // Collapse all nodes with children (except root) initially
    root.descendants().forEach((d, i) => {
        if (d.depth > 1 && d.children) {
            d._children = d.children;
            d.children = null;
        }
    });

    update(root);

    // Center the root
    svg.call(zoom.transform, d3.zoomIdentity.translate(width() / 2 - root.x, 60));
}

// --- Update tree ---
function update(source) {
    const duration = DURATION;

    treeLayout(root);
    const nodes = root.descendants();
    const links = root.links();

    // Normalize y spacing for top-down layout. X (breadth) is handled by tree.size().
nodes.forEach(d => { d.y = d.depth * (NODE_HEIGHT + 100); });

    // --- Links ---
    const link = g.selectAll(".link")
        .data(links, d => d.target.data.id);

    const linkEnter = link.enter()
        .append("path")
        .attr("class", "link")
        .attr("d", d => {
            const o = { x: source.x0, y: source.y0 };
            return diagonal({ source: o, target: o });
        });

    link.merge(linkEnter)
        .transition().duration(duration)
        .attr("d", diagonal);

    link.exit()
        .transition().duration(duration)
        .attr("d", d => {
            const o = { x: source.x, y: source.y };
            return diagonal({ source: o, target: o });
        })
        .remove();

    // --- Nodes ---
    const node = g.selectAll(".node")
        .data(nodes, d => d.data.id);

    const nodeEnter = node.enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${source.x0},${source.y0})`)
        .on("click", (event, d) => {
            event.stopPropagation();
            handleNodeClick(d);
        });

    // Node rectangle
    nodeEnter.append("rect")
        .attr("width", NODE_WIDTH)
        .attr("height", NODE_HEIGHT)
        .attr("x", -NODE_WIDTH / 2)
        .attr("y", -NODE_HEIGHT / 2)
        .attr("rx", 8);

    // Gender indicator bar (left edge)
    nodeEnter.append("rect")
        .attr("class", "gender-bar")
        .attr("width", 5)
        .attr("height", NODE_HEIGHT)
        .attr("x", -NODE_WIDTH / 2)
        .attr("y", -NODE_HEIGHT / 2)
        .attr("rx", 2);

    // Name text
    nodeEnter.append("text")
        .attr("class", "name-text")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.35em")
        .attr("y", -4)
        .text(d => d.data.name + vitalBadge(d));

    // Spouse text (if any)
    nodeEnter.append("text")
        .attr("class", "spouse-text")
        .attr("text-anchor", "middle")
        .attr("dy", "1.2em")
        .attr("y", -4)
        .text(d => d.data.spouse_name ? `+ ${d.data.spouse_name}` : "");

    // Expand/collapse toggle circle (below node for top-down layout)
    nodeEnter.append("circle")
        .attr("class", "toggle-circle")
        .attr("r", 0)
        .attr("cx", 0)
        .attr("cy", NODE_HEIGHT / 2 + 12)
        .style("fill", "#fff")
        .style("stroke", "#3498db")
        .style("stroke-width", 1.5)
        .style("cursor", "pointer");

    nodeEnter.append("text")
        .attr("class", "toggle-text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("x", 0)
        .attr("y", NODE_HEIGHT / 2 + 12)
        .style("font-size", "11px")
        .style("fill", "#3498db")
        .style("pointer-events", "none");

    // Merge and transition
    const nodeUpdate = node.merge(nodeEnter);

    nodeUpdate.transition().duration(duration)
        .attr("transform", d => `translate(${d.x},${d.y})`);

    // Update colors
    nodeUpdate.select("rect:first-of-type")
        .attr("fill", d => d._children ? "#e8f4fd" : "#fff");

    nodeUpdate.select(".gender-bar")
        .attr("fill", nodeColor);

    // Update toggle indicators
    nodeUpdate.select(".toggle-circle")
        .attr("r", d => {
            const hasChildren = d.children || d._children;
            return hasChildren ? 10 : 0;
        });

    nodeUpdate.select(".toggle-text")
        .text(d => d.children ? "−" : (d._children ? "+" : ""))
        .attr("y", NODE_HEIGHT / 2 + 12);

    // Refresh selected state
    nodeUpdate.classed("selected", d => d.data.id === selectedNodeId);

    // Exit
    const nodeExit = node.exit()
        .transition().duration(duration)
        .attr("transform", d => `translate(${source.x},${source.y})`)
        .remove();

    nodeExit.select("rect")
        .attr("width", 0);

    // Store old positions for transitions
    root.each(d => {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

// --- Diagonal path generator (top-to-bottom) ---
function diagonal(d) {
    return `M ${d.source.x} ${d.source.y}
            C ${d.source.x} ${(d.source.y + d.target.y) / 2},
              ${d.target.x} ${(d.source.y + d.target.y) / 2},
              ${d.target.x} ${d.target.y}`;
}

// --- Node click handler ---
async function handleNodeClick(d) {
    // Toggle children
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    update(d);

    // Show details
    selectedNodeId = d.data.id;
    showMemberDetails(d.data.id);
}

// --- Detail panel ---
async function showMemberDetails(id) {
    try {
        const resp = await fetch(`/api/member/${id}`);
        const member = await resp.json();

        if (member.error) return;

        document.getElementById("detail-placeholder").style.display = "none";
        document.getElementById("detail-content").style.display = "block";

        document.getElementById("detail-name").textContent = member.name;
        document.getElementById("detail-gender").textContent = member.gender;
        document.getElementById("detail-status").textContent = member.vital_stats || "—";
        document.getElementById("detail-spouse").textContent = member.spouse_name || "—";

        const parentsList = member.parents && member.parents.length > 0
            ? member.parents.map(p => p.name).join(", ")
            : "—";
        document.getElementById("detail-parents").textContent = parentsList;

        const childrenList = member.children_names && member.children_names.length > 0
            ? member.children_names.join(", ")
            : "—";
        document.getElementById("detail-children").textContent = childrenList;

        // Highlight selected node in tree
        g.selectAll(".node").classed("selected", d => d.data.id === id);
    } catch (err) {
        console.error("Failed to fetch member details:", err);
    }
}

// --- Search ---
let searchTimeout;
const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");

searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    const query = searchInput.value.trim();
    if (!query) {
        searchResults.classList.remove("active");
        return;
    }
    searchTimeout = setTimeout(() => doSearch(query), 250);
});

searchInput.addEventListener("focus", () => {
    if (searchInput.value.trim()) {
        searchResults.classList.add("active");
    }
});

document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-box")) {
        searchResults.classList.remove("active");
    }
});

async function doSearch(query) {
    try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await resp.json();

        searchResults.innerHTML = "";
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="result-item" style="color:#999;">No results</div>';
        } else {
            results.forEach(r => {
                const div = document.createElement("div");
                div.className = "result-item";
                div.innerHTML = `
                    <div class="result-name">${r.name}</div>
                    <div class="result-meta">${r.gender} · ${r.vital_stats || "—"}</div>
                `;
                div.addEventListener("click", () => {
                    searchResults.classList.remove("active");
                    searchInput.value = "";
                    focusNode(r.id);
                });
                searchResults.appendChild(div);
            });
        }
        searchResults.classList.add("active");
    } catch (err) {
        console.error("Search failed:", err);
    }
}

function findNodeById(node, id) {
    if (node.data.id === id) return node;
    const kids = node.children || node._children;
    if (kids) {
        for (const child of kids) {
            const found = findNodeById(child, id);
            if (found) return found;
        }
    }
    return null;
}

async function focusNode(id) {
    // Search both visible (children) and collapsed (_children) subtrees
    let node = findNodeById(root, id);

    // If not found as a tree node, this person may be a spouse
    // (spouses are shown as labels on their partner's card, not as separate nodes)
    if (!node) {
        try {
            const resp = await fetch(`/api/member/${id}`);
            const member = await resp.json();
            if (member.spouse) {
                // Focus on the partner's node instead
                id = member.spouse;
                node = findNodeById(root, id);
            }
        } catch (err) {
            console.error("Failed to fetch member for spouse lookup:", err);
        }
    }

    if (!node) return;

    // Expand all ancestors so the node becomes visible
    let current = node;
    while (current) {
        if (current._children) {
            current.children = current._children;
            current._children = null;
        }
        current = current.parent;
    }

    update(node);

    // Pan to center the node on screen
    const transform = d3.zoomIdentity
        .translate(width() / 2 - node.x, height() / 2 - node.y)
        .scale(1);

    svg.transition().duration(750).call(zoom.transform, transform);

    // Show details
    selectedNodeId = id;
    showMemberDetails(id);
}

// --- Toolbar buttons ---
document.getElementById("reset-btn").addEventListener("click", () => {
    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(width() / 2 - root.x0, 60));
    selectedNodeId = null;
    g.selectAll(".node").classed("selected", false);
    document.getElementById("detail-placeholder").style.display = "";
    document.getElementById("detail-content").style.display = "none";
});

document.getElementById("expand-all-btn").addEventListener("click", () => {
    root.descendants().forEach(d => {
        if (d._children) {
            d.children = d._children;
            d._children = null;
        }
    });
    update(root);
});

document.getElementById("collapse-all-btn").addEventListener("click", () => {
    root.descendants().forEach(d => {
        if (d.depth > 0 && d.children) {
            d._children = d.children;
            d.children = null;
        }
    });
    update(root);
});

// --- Handle window resize ---
window.addEventListener("resize", () => {
    svg.attr("width", width()).attr("height", height());
    treeLayout.size([width() - 40, height() - 120]);
    update(root);
});

// --- Click on SVG background to deselect ---
svg.on("click", () => {
    selectedNodeId = null;
    g.selectAll(".node").classed("selected", false);
    document.getElementById("detail-placeholder").style.display = "";
    document.getElementById("detail-content").style.display = "none";
});

// --- Initialize ---
init();
