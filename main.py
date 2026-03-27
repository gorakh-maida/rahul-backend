<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rahul Maida - Premium</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { background: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
        .course-card { background: #0f172a; border: 1px solid #1e293b; transition: 0.3s; }
        .course-card:hover { border-color: #fbbf24; transform: scale(1.02); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <nav class="flex justify-between items-center mb-10 border-b border-white/5 pb-4">
            <h1 onclick="location.reload()" class="text-2xl font-black text-yellow-400 cursor-pointer italic">RAHUL <span class="text-white">MAIDA</span></h1>
            <div id="btn-box"></div>
        </nav>

        <div id="main-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div class="col-span-full text-center py-20 font-bold animate-pulse text-slate-500">INITIATING RAHUL'S API...</div>
        </div>

        <!-- Hidden Debug Box -->
        <div id="debug" class="mt-20 p-4 bg-slate-900 rounded text-[9px] text-slate-600 font-mono"></div>
    </div>

    <script>
        const API = "https://rahul-backend-7ag5.onrender.com";
        let store = [];

        async function fetchAll() {
            const grid = document.getElementById('main-grid');
            try {
                const res = await fetch(`${API}/api/batches`);
                store = await res.json();
                
                grid.innerHTML = store.map(b => {
                    // AUTO-DETECT ID: If batchId missing, look for .id
                    const realId = b.batchId || b.id || b._id; 
                    return `
                    <div onclick="openDetails('${realId}')" class="course-card rounded-2xl overflow-hidden cursor-pointer">
                        <img src="${b.batchImage}" class="w-full h-40 object-cover opacity-80">
                        <div class="p-4">
                            <h3 class="font-bold text-xs h-8 line-clamp-2 leading-relaxed">${b.batchName}</h3>
                            <button class="mt-4 w-full bg-slate-800 text-yellow-400 py-2 rounded-lg text-[9px] font-black uppercase tracking-widest border border-yellow-500/20">Click To Open</button>
                        </div>
                    </div>`;
                }).join('');
                lucide.createIcons();
            } catch (e) { grid.innerHTML = "Server Busy. Reload."; }
        }

        async function openDetails(bid) {
            const grid = document.getElementById('main-grid');
            grid.innerHTML = "<div class='col-span-full text-center py-10 text-yellow-500'>Opening Batch Files...</div>";
            
            try {
                const res = await fetch(`${API}/api/details/${bid}`);
                const resData = await res.json();
                
                // Debugging
                document.getElementById('debug').innerHTML = `Last Data Loaded for ID ${bid}: ` + JSON.stringify(resData).substring(0, 300);

                let subjects = [];
                if (resData.data && resData.data.subjects) subjects = resData.data.subjects;
                else if (Array.isArray(resData.data)) subjects = resData.data;
                else if (Array.isArray(resData)) subjects = resData;

                document.getElementById('btn-box').innerHTML = `<button onclick="location.reload()" class="bg-white text-black px-4 py-1 rounded-xl text-[10px] font-black">BACK HOME</button>`;

                if (subjects.length === 0) {
                    grid.innerHTML = `<div class="col-span-full text-center py-20 bg-slate-800/30 rounded-3xl">
                        <p class="text-sm font-bold text-slate-400">Empty or Protected Content</p>
                        <p class="text-[10px] text-slate-600 mt-2 italic">Try a different batch or wait for sync.</p>
                    </div>`;
                    return;
                }

                grid.innerHTML = subjects.map(s => `
                    <div onclick="openContent('${bid}', '${s.subjectId}')" class="bg-slate-800/50 p-6 rounded-2xl flex items-center gap-4 cursor-pointer border border-white/5 hover:border-yellow-400 transition-all">
                        <div class="text-yellow-400"><i data-lucide="folder-lock"></i></div>
                        <span class="font-bold text-xs truncate">${s.subjectName}</span>
                    </div>
                `).join('');
                lucide.createIcons();
            } catch (e) { alert("Error on detail load."); }
        }

        async function openContent(bid, sid) {
            const grid = document.getElementById('main-grid');
            grid.innerHTML = "<div class='col-span-full py-10 text-center animate-pulse'>Fetching Lessons...</div>";
            
            try {
                const res = await fetch(`${API}/api/content/${bid}/${sid}`);
                const resData = await res.json();
                const items = resData.data || (Array.isArray(resData) ? resData : []);

                document.getElementById('btn-box').innerHTML = `<button onclick="openDetails('${bid}')" class="bg-white text-black px-4 py-1 rounded-xl text-[10px] font-black">BACK TO SUBJECTS</button>`;

                if (items.length === 0) {
                    grid.innerHTML = "<div class='col-span-full text-center py-20 text-slate-500'>Lessons are being uploaded...</div>";
                    return;
                }

                grid.innerHTML = items.map(i => `
                    <div class="course-card p-5 rounded-3xl flex flex-col justify-between">
                        <div>
                            <div class="h-10 w-10 flex items-center justify-center rounded-xl bg-slate-800 text-yellow-400 mb-4">
                                <i data-lucide="${i.url.includes('.pdf') ? 'file-text' : 'youtube'}"></i>
                            </div>
                            <h4 class="text-[11px] font-bold line-clamp-2">${i.title}</h4>
                        </div>
                        <a href="${i.url}" target="_blank" class="mt-6 block w-full text-center bg-yellow-400 text-black py-3 rounded-2xl font-black text-[10px] uppercase shadow-lg shadow-yellow-400/10">GO TO LESSON</a>
                    </div>
                `).join('');
                lucide.createIcons();
            } catch (e) { alert("Error on content load."); }
        }

        window.onload = fetchAll;
    </script>
</body>
</html>
