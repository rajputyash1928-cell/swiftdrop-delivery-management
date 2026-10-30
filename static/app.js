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
        map: 'Monitor simulated delivery drivers across Pune.',
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
            ${s.delivered} of ${s.total} orders are marked as delivered.
        </div>

        <div class="insight">
            <b>Fleet utilization</b>
            ${s.active_drivers} drivers are currently assigned to deliveries.
        </div>

        <div class="insight">
            <b>Route planning</b>
            Use route planning to generate a suggested sequence.
        </div>
    `;

    renderOrders();
    renderDrivers();
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

            <td>
                ${o.priority >= 4 ? 'Urgent' : o.priority >= 3 ? 'High' : 'Normal'}
            </td>

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

                        <small>
                            ${i === 0 ? 'Dispatch origin' : 'Stop ' + i}
                        </small>

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
   REAL PUNE DEMO LIVE MAP
========================================== */

let puneMap = null;
let puneDriver = null;
let puneAnimation = null;
let puneRunning = false;
let puneProgress = 0;
let puneLastTime = 0;

const puneLocations = [

    {
        name: 'Warehouse',
        position: [18.5289, 73.8744],
        type: 'warehouse'
    },

    {
        name: 'Shivajinagar',
        position: [18.5308, 73.8475],
        type: 'customer'
    },

    {
        name: 'Deccan',
        position: [18.5158, 73.8419],
        type: 'customer'
    },

    {
        name: 'Kothrud',
        position: [18.5074, 73.8077],
        type: 'customer'
    },

    {
        name: 'Swargate',
        position: [18.5018, 73.8636],
        type: 'customer'
    },

    {
        name: 'Hadapsar',
        position: [18.5089, 73.9260],
        type: 'customer'
    }

];

let puneRouteCoordinates = puneLocations.map(
    location => location.position
);


function renderDemoMap() {

    const mapElement = $('demoMap');

    if (!mapElement) return;

    if (typeof L === 'undefined') {

        mapElement.innerHTML =
            '<div class="empty-state">Map library could not load. Please refresh the page.</div>';

        return;
    }

    if (!puneMap) {

        mapElement.innerHTML = '';

        puneMap = L.map('demoMap').setView(
            [18.5204, 73.8567],
            12
        );

        L.tileLayer(
            'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }
        ).addTo(puneMap);


        // Add warehouse and customer markers.

        puneLocations.forEach(location => {

            const icon = L.divIcon({

                className: '',

                html: location.type === 'warehouse'
                    ? '<div style="font-size:25px">🏭</div>'
                    : '<div style="font-size:23px">📍</div>',

                iconSize: [30, 30],

                iconAnchor: [15, 15]

            });

            L.marker(location.position, { icon })
                .addTo(puneMap)
                .bindPopup(`
                    <b>${location.name}</b><br>
                    ${location.type === 'warehouse'
                        ? 'Delivery warehouse'
                        : 'Customer delivery location'}
                `);

        });


        // Display the suggested sample route.

        L.polyline(puneRouteCoordinates, {

            color: '#3568e8',
            weight: 5,
            opacity: 0.8,
            dashArray: '10, 10'

        }).addTo(puneMap);


        // Create moving truck marker.

        const truckIcon = L.divIcon({

            className: '',

            html: '<div style="font-size:28px">🚚</div>',

            iconSize: [35, 35],

            iconAnchor: [17, 17]

        });

        puneDriver = L.marker(
            puneRouteCoordinates[0],
            { icon: truckIcon }
        ).addTo(puneMap);

        puneDriver.bindPopup('<b>SwiftDrop Demo Driver</b>');


        $('mapStops').textContent = '5';
        $('mapDrivers').textContent = '1';

        $('mapDeliveryStatus').textContent = 'Ready';
        $('mapStatus').textContent = '● Simulation ready';

    }

    setTimeout(() => {
        puneMap.invalidateSize();
    }, 250);

}


function startDemoMap() {

    if (!puneMap) {
        renderDemoMap();
    }

    if (!puneDriver || puneRunning) return;

    puneRunning = true;
    puneLastTime = 0;

    $('mapStatus').textContent = '● Driver moving';
    $('mapDeliveryStatus').textContent = 'In transit';

    puneAnimation = requestAnimationFrame(movePuneDriver);

}


function movePuneDriver(timestamp) {

    if (!puneRunning) return;

    if (!puneLastTime) {
        puneLastTime = timestamp;
    }

    const delta = timestamp - puneLastTime;

    puneLastTime = timestamp;

    // Complete the sample route in approximately 60 seconds.

    puneProgress += delta / 60000;

    if (puneProgress >= 1) {
        puneProgress = 0;
    }

    const totalSegments = puneRouteCoordinates.length - 1;

    const position = puneProgress * totalSegments;

    const segment = Math.min(
        Math.floor(position),
        totalSegments - 1
    );

    const fraction = position - segment;

    const start = puneRouteCoordinates[segment];
    const end = puneRouteCoordinates[segment + 1];

    const lat = start[0] + (end[0] - start[0]) * fraction;
    const lng = start[1] + (end[1] - start[1]) * fraction;

    puneDriver.setLatLng([lat, lng]);

    $('mapDeliveryStatus').textContent =
        'Stop ' + (segment + 1) + ' of ' + totalSegments;

    puneAnimation = requestAnimationFrame(movePuneDriver);

}


function pauseDemoMap() {

    puneRunning = false;

    if (puneAnimation) {

        cancelAnimationFrame(puneAnimation);

        puneAnimation = null;

    }

    puneLastTime = 0;

    $('mapStatus').textContent = 'Ⅱ Simulation paused';

    $('mapDeliveryStatus').textContent = 'Paused';

}


function resetDemoMap() {

    pauseDemoMap();

    puneProgress = 0;

    if (puneDriver) {

        puneDriver.setLatLng(
            puneRouteCoordinates[0]
        );

    }

    $('mapStatus').textContent = '● Simulation reset';

    $('mapDeliveryStatus').textContent = 'Ready';

    toast('Pune demo map reset successfully.');

}


/* INITIAL LOAD */

$('today').textContent = new Intl.DateTimeFormat('en-IN', {

    day: '2-digit',
    month: 'short',
    year: 'numeric'

}).format(new Date());

loadData();
