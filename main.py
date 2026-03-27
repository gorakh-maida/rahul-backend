<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rahul Maida Study</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>body { background: #0f172a; color: white; }</style>
</head>
<body class="p-5">
    <div class="max-w-5xl mx-auto">
        <header class="flex justify-between items-center mb-8">
            <h1 onclick="location.reload()" class="text-2xl font-black text-yellow-400 cursor-pointer">RAHUL MAIDA</h1>
            <div id="nav"></div>
        </header>

        <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="col-span-full text-center py-20 animate-pulse text-slate-500">Connecting to Rahul's API...</div>
        </div>
    </div>

    <script>
        const API = "https://rahul-backend-7ag5.onrender.com";

        async function start() {
            const res = await fetch(`${API}/api/batches`);
            const data = await res.json();
            const grid = document.getElementById('grid');
            
            grid.innerHTML = data.map(b => `
                <div onclick="openBatch('${b.batchId}')" class="bg-slate-800 border border-white/5 p-4 rounded-2xl cursor-pointer hover:border-yellow-400">
                    <img src="${b.batchImage}" class="w-full h-40 object-cover rounded-xl mb-4">
                    <h3 class="font-bold text-sm">${b.batchName}</h3>
                </div>
            `).join('');
        }

        async function openBatch(bid) {
            const grid = document.getElementById('grid');
            grid.innerHTML = "<div class='col-span-full py-20 text-center text-yellow-500 font-bold'>FETCHING SUBJECTS...</div>";
            
            try {
                const res = await fetch(`${API}/api/details/${bid}`);
                const resData = await res.json();
                
                // BACKUP DATA CHECK: Agar data.subjects khali hai toh data pure array ko check karo
                let subjects = (resData.data && resData.data.subjects) ? resData.data.subjects : (resData.data || []);

                document.getElementById('nav').innerHTML = `<button onclick="location.reload()" class="bg-white text-black px-4 py-1 rounded-lg font-bold">BACK</button>`;

                if (subjects.length === 0) {
                    grid.innerHTML = "<div class='col-span-full text-center py-20'>No Subjects Found. Try another batch.</div>";
                    return;
                }

                grid.innerHTML = subjects.map(s => `
                    <div onclick="openContent('${bid}', '${s.subjectId}')" class="bg-slate-800 p-6 rounded-2xl border border-white/5 flex items-center gap-4 cursor-pointer hover:bg-slate-700">
                        <div class="h-10 w-10 bg-yellow-500/20 rounded flex items-center justify-center text-yellow-500">
                            <i data-lucide="folder"></i>
                        </div>
                        <span class="font-bold text-sm">${s.subjectName}</span>
                    </div>
                `).join('');
                lucide.createIcons();
            } catch(e) { grid.innerHTML = "Error loading details."; }
        }

        async function openContent(bid, sid) {
            const grid = document.getElementById('grid');
            grid.innerHTML = "<div class='col-span-full py-20 text-center'>LOADING...</div>";

            try {
                const res = await fetch(`${API}/api/content/${bid}/${sid}`);
                const data = await res.json();
                const content = data.data || [];

                grid.innerHTML = content.map(item => `
                    <div class="bg-slate-800 border border-white/5 p-5 rounded-2xl flex flex-col justify-between">
                        <h4 class="text-sm font-bold mb-4">${item.title}</h4>
                        <a href="${item.url}" target="_blank" class="block w-full text-center bg-yellow-400 text-black py-2 rounded-xl font-bold text-[10px]">OPEN NOW</a>
                    </div>
                `).join('');
                lucide.createIcons();
            } catch(e) { grid.innerHTML = "No content here."; }
        }

        window.onload = start;
    </script>
</body>
</html>
