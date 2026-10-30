let state = {
    orders: [],
    drivers: [],
    locations: [],
    stats: {}
};

const $ = id => document.getElementById(id);

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
}[c]));

function toast(msg) {
    const el = $('toast');
    el.textContent = msg;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 2600);
}

/* NAVIGATION */

function showView(id) {
    document.querySelectorAll('.view').forEach(x =>
        x.classList.toggle('active', x.id === id)
    );

    document.querySelectorAll('.nav').forEach(x =>
        x.classList.toggle('active', x.dataset.view === id)
    );

    const titles = {
        overview: 'Overview',
        orders: 'Order management',
        drivers: 'Driver management',
        routes: 'Route planning',
        map: 'Demo Live Map',
        analytics: 'Performance analytics'
    };

    const descriptions = {
        orders: 'Review customer requests and keep every delivery moving.',
        drivers: 'Monitor your delivery team and current assignments.',
        routes: 'Plan efficient dispatch sequences for active orders.',
        map: 'Monitor simulated delivery drivers and customer locations.',
        analytics: 'A quick view of delivery service performance.'
    };

    $('crumb').textContent = titles[id];

    $('pageTitle').innerHTML =
        id === 'overview'
            ? 'Good afternoon, team <span>✦</span>'
            : titles[id];

    document.querySelector('.topbar p').textContent =
        id === 'overview'
            ? 'Here’s what’s happening with your deliveries today.'
            : descriptions[id];

    if (id === 'orders') renderOrders();
    if (id === 'drivers') renderDrivers();
    if (id === 'map') renderDemoMap();
}

document.querySelectorAll('.nav').forEach(b => {
    b.addEventListener('click', () => showView(b.dataset.view));
});

/* API */

async function api(url, opts = {}) {
    const r = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...opts
    });

    const d = await r.json();

    if (!r.ok) {
        throw Error(d.error || 'Something went wrong');
    }

    return d;
}

async function loadData() {
    try {
        state = await api('/api/operations');
        renderAll();
    } catch (e) {
        toast(e.message);
    }
}

/* DASHBOARD */

function renderAll() {
    const s = state.stats;

    $('mTotal').textContent = s.total;
    $('mDelivered').textContent = s.delivered;
    $('mTransit').textContent = s.transit;
    $('mPending').textContent = s.pending;

    $('donutTotal').textContent = s.total;
    $('lDelivered').textContent = s.delivered;
    $('lTransit').textContent = s.transit;
    $('lPending').textContent = s.pending;

    const a = s.total ? s.delivered / s.total * 100 : 0;
    const b = s.total ? s.transit / s.total * 100 : 0;

    $('donut').style.background =
        `conic-gradient(#16a477 0 ${a}%,#ee9b38 ${a}% ${a + b}%,#8c6be8 ${a + b}% 100%)`;

    $('fleetSummary').innerHTML = state.drivers.map(d => `
        <div class="fleet-line">
            <div class="fleet-avatar">
                ${esc(d.name.split(' ').map(x => x[0]).join(''))}
            </div>
            <div>
                <b>${esc(d.name)}</b>
                <small>${esc(d.vehicle)} · ${esc(d.id)}</small>
            </div>
            <span class="status-pill"
                style="${d.status === 'Available' ? 'background:#eef2ff;color:#5275d5' : ''}">
                ${esc(d.status)}
            </span>
        </div>
    `).join('');

    $('recentRows').innerHTML =
        state.orders.slice(0, 5).map(orderRow).join('') ||
        '<tr><td colspan="6">No orders yet.</td></tr>';

    $('locationSelect').innerHTML =
        state.locations
            .filter(l => l.id !== 'W')
            .map(l => `<option value="${esc(l.id)}">${esc(l.name)}</option>`)
            .join('');

    $('aDelivered').textContent = s.delivered;
    $('aDrivers').textContent = s.active_drivers;
    $('aSaved').textContent = s.distance_saved + ' km';

    $('insights').innerHTML = `
        <div class="insight">
            <b>Dispatch queue</b>
            ${s.pending} orders are waiting to be assigned.
            Prioritize high-priority parcels first.
        </div>

        <div class="insight">
            <b>Delivery progress</b>
            ${s.delivered} of ${s.total} orders are marked as delivered
            in this demo dataset.
        </div>

        <div class="insight">
            <b>Fleet utilization</b>
            ${s.active_drivers} drivers are currently assigned to deliveries.
        </div>

        <div class="insight">
            <b>Route planning</b>
            Use route planning to generate a suggested sequence
            for all active stops.
        </div>
    `;

    renderOrders();
    renderDrivers();

    if ($('map')?.classList.contains('active')) {
        renderDemoMap();
    }
}

/* ORDERS */

function badge(status) {
    return `<span class="badge ${status.replace(' ', '.')}">${esc(status)}</span>`;
}

function driverName(id) {
    return state.drivers.find(d => d.id === id)?.name || id || 'Unassigned';
}

function orderRow(o) {
    return `
        <tr>
            <td>${esc(o.id)}</td>
            <td>${esc(o.customer)}</td>
            <td>${esc(o.address)}</td>
            <td>${esc(o.weight)} kg</td>
            <td>${o.priority >= 4 ? 'Urgent' : o.priority >= 3 ? 'High' : 'Normal'}</td>

            <td>
                <select aria-label="Assign driver"
                    onchange="updateOrder('${esc(o.id)}',{driver_id:this.value})">

                    <option value="Unassigned"
                        ${o.driver_id === 'Unassigned' ? 'selected' : ''}>
                        Unassigned
                    </option>

                    ${state.drivers.map(d => `
                        <option value="${esc(d.id)}"
                            ${o.driver_id === d.id ? 'selected' : ''}>
                            ${esc(d.name)}
                        </option>
                    `).join('')}

                </select>
            </td>

            <td>${badge(o.status)}</td>

            <td>
                <select aria-label="Update status"
                    onchange="updateOrder('${esc(o.id)}',{status:this.value})">

                    <option selected disabled>Update</option>

                    ${['Pending', 'In Transit', 'Delivered', 'Cancelled']
                        .map(x => `<option>${x}</option>`).join('')}

                </select>
            </td>
        </tr>
    `;
}

function renderOrders() {
    if (!$('orderRows')) return;

    const q = ($('orderSearch')?.value || '').toLowerCase();
    const f = $('statusFilter')?.value || 'All';

    const rows = state.orders.filter(o =>
        (f === 'All' || o.status === f) &&
        [o.id, o.customer, o.address].join(' ').toLowerCase().includes(q)
    );

    $('orderRows').innerHTML =
        rows.map(orderRow).join('') ||
        '<tr><td colspan="8">No matching orders.</td></tr>';
}

/* DRIVERS */

function renderDrivers() {
    $('driverCards').innerHTML = state.drivers.map(d => {

        const assigned = state.orders.filter(o =>
            o.driver_id === d.id &&
            o.status !== 'Delivered' &&
            o.status !== 'Cancelled'
        ).length;

        return `
            <article class="driver-card">

                <div class="driver-top">
                    <div class="driver-big">
                        ${esc(d.name.split(' ').map(x => x[0]).join(''))}
                    </div>

                    <div>
                        <b>${esc(d.name)}</b>
                        <small>${esc(d.id)} · ${esc(d.phone)}</small>
                    </div>
                </div>

                <div class="driver-meta">

                    <div>
                        <small>Vehicle</small>
                        <b>${esc(d.vehicle)}</b>
                    </div>

                    <div>
                        <small>Load capacity</small>
                        <b>${d.capacity} kg</b>
                    </div>

                    <div>
                        <small>Current orders</small>
                        <b>${assigned}</b>
                    </div>

                    <div>
                        <small>Availability</small>
                        <b>${esc(d.status)}</b>
                    </div>

                </div>

            </article>
        `;
    }).join('');
}

/* CREATE ORDER */

function openOrderForm() {
    $('orderModal').classList.add('show');
}

function closeOrderForm() {
    $('orderModal').classList.remove('show');
}

$('orderForm').addEventListener('submit', async e => {
    e.preventDefault();

    try {
        const data = Object.fromEntries(new FormData(e.target));

        await api('/api/orders', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        e.target.reset();
        closeOrderForm();

        await loadData();

        showView('orders');
        toast('New delivery order created.');

    } catch (err) {
        toast(err.message);
    }
});

/* UPDATE ORDER */

async function updateOrder(id, data) {
    try {
        await api('/api/orders/' + id, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });

        await loadData();

        toast('Order details updated.');

    } catch (e) {
        toast(e.message);
    }
}

/* ROUTE OPTIMIZATION */

async function optimizeRoute() {
    try {
        const d = await api('/api/route/optimize', {
            method: 'POST',
            body: '{}'
        });

        $('routeStops').textContent = d.stops;
        $('routeDistance').textContent = d.distance + ' km';
        $('routeStatus').textContent = 'Generated';

        $('routeCanvas').innerHTML = `
            <div class="route-flow">

                ${d.route.map((id, i) => `
                    <div class="route-stop">
                        <b>
                            ${i === 0
                                ? 'Warehouse'
                                : esc(state.locations.find(l => l.id === id)?.name || id)}
                        </b>
                        <small>${i === 0 ? 'Dispatch origin' : 'Stop ' + i}</small>
                    </div>

                    ${i < d.route.length - 1
                        ? '<span class="route-arrow">→</span>'
                        : ''}

                `).join('')}

            </div>
        `;

        toast('Suggested delivery route generated.');

    } catch (e) {
        toast(e.message);
    }
}


/* ==========================================
   DEMO LIVE MAP
========================================== */

let mapRunning = false;
let mapFrame = null;
let mapProgress = 0;
let mapLastTime = 0;
let mapRoute = [];
let mapPoints = [];

const MAP_WIDTH = 1000;
const MAP_HEIGHT = 600;

function getMapCoordinates() {

    const locations = state.locations || [];

    if (!locations.length) return [];

    const xs = locations.map(l => Number(l.x) || 0);
    const ys = locations.map(l => Number(l.y) || 0);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    return locations.map((location, index) => {

        let x = Number(location.x) || 0;
        let y = Number(location.y) || 0;

        return {
            ...location,
            px: 90 + ((x - minX) / rangeX) * 820,
            py: 80 + ((maxY - y) / rangeY) * 440
        };
    });
}

function renderDemoMap() {

    const map = $('demoMap');

    if (!map || !state.locations.length) {
        if (map) {
            map.innerHTML = '<div class="empty-state">No map locations available.</div>';
        }
        return;
    }

    mapPoints = getMapCoordinates();

    const warehouse = mapPoints.find(l => l.id === 'W');

    const customers = mapPoints.filter(l => l.id !== 'W');

    if (!warehouse || !customers.length) {
        map.innerHTML = '<div class="empty-state">Warehouse or customer locations are missing.</div>';
        return;
    }

    mapRoute = [warehouse, ...customers, warehouse];

    const roadLines = customers.map(customer => `
        <line class="map-road"
            x1="${warehouse.px}" y1="${warehouse.py}"
            x2="${customer.px}" y2="${customer.py}" />
    `).join('');

    const routePoints = mapRoute.map(p => `${p.px},${p.py}`).join(' ');

    map.innerHTML = `

        <svg viewBox="0 0 ${MAP_WIDTH} ${MAP_HEIGHT}"
             preserveAspectRatio="none">

            ${roadLines}

            <polyline
                class="map-route"
                points="${routePoints}" />

        </svg>

        ${mapPoints.map(location => {

            const isWarehouse = location.id === 'W';

            return `
                <div class="map-marker ${isWarehouse ? 'warehouse' : 'customer'}"
                    style="left:${location.px / MAP_WIDTH * 100}%;
                           top:${location.py / MAP_HEIGHT * 100}%">

                    <span>${isWarehouse ? '🏭' : '📍'}</span>

                    ${esc(location.name)}

                </div>
            `;
        }).join('')}

        <div class="map-marker driver" id="movingDriver"
            style="left:${warehouse.px / MAP_WIDTH * 100}%;
                   top:${warehouse.py / MAP_HEIGHT * 100}%">

            <span>🚚</span>
            Demo Driver

        </div>

    `;

    $('mapStops').textContent = customers.length;
    $('mapDrivers').textContent = 1;

    if (!mapRunning) {
        $('mapDeliveryStatus').textContent = 'Ready';
        $('mapStatus').textContent = '● Simulation ready';
    }

    updateDriverPosition();
}

function updateDriverPosition() {

    const driver = $('movingDriver');

    if (!driver || mapRoute.length < 2) return;

    const totalSegments = mapRoute.length - 1;

    const totalProgress = mapProgress * totalSegments;

    const segment = Math.min(
        Math.floor(totalProgress),
        totalSegments - 1
    );

    const fraction = totalProgress - segment;

    const start = mapRoute[segment];
    const end = mapRoute[segment + 1];

    const x = start.px + (end.px - start.px) * fraction;
    const y = start.py + (end.py - start.py) * fraction;

    driver.style.left = (x / MAP_WIDTH * 100) + '%';
    driver.style.top = (y / MAP_HEIGHT * 100) + '%';

    if (mapProgress >= 1) {
        $('mapDeliveryStatus').textContent = 'Route completed';
    } else {
        $('mapDeliveryStatus').textContent =
            'Stop ' + Math.min(segment + 1, totalSegments) +
            ' of ' + totalSegments;
    }
}

function animateDriver(timestamp) {

    if (!mapRunning) return;

    if (!mapLastTime) mapLastTime = timestamp;

    const delta = timestamp - mapLastTime;

    mapLastTime = timestamp;

    // Full route takes approximately 40 seconds.
    mapProgress += delta / 40000;

    if (mapProgress >= 1) {
        mapProgress = 0;
    }

    updateDriverPosition();

    mapFrame = requestAnimationFrame(animateDriver);
}

function startDemoMap() {

    if (!mapRoute.length) {
        renderDemoMap();
    }

    if (mapRoute.length < 2) {
        toast('Map locations are not available.');
        return;
    }

    if (mapRunning) return;

    mapRunning = true;
    mapLastTime = 0;

    $('mapStatus').textContent = '● Driver moving';
    $('mapDeliveryStatus').textContent = 'In progress';

    mapFrame = requestAnimationFrame(animateDriver);

    toast('Demo delivery simulation started.');
}

function pauseDemoMap() {

    mapRunning = false;

    if (mapFrame) {
        cancelAnimationFrame(mapFrame);
        mapFrame = null;
    }

    mapLastTime = 0;

    $('mapStatus').textContent = 'Ⅱ Simulation paused';
    $('mapDeliveryStatus').textContent = 'Paused';

    toast('Demo simulation paused.');
}

function resetDemoMap() {

    pauseDemoMap();

    mapProgress = 0;

    renderDemoMap();

    $('mapStatus').textContent = '● Simulation reset';
    $('mapDeliveryStatus').textContent = 'Ready';

    toast('Demo map reset successfully.');
}


/* DATE AND INITIAL LOAD */

$('today').textContent = new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
}).format(new Date());

loadData();
