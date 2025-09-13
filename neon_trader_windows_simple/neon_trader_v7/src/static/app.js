class App {
    constructor() {
        this.sessionToken = null;
        this.currentUser = null;
        this.vaultUnlocked = false;
        this.init();
    }

    init() {
        console.log("App initialized. Bypassing login for development.");
        this.showMainApp();
        this.setupEventListeners();
        this.updateUserInfo();
        this.checkVaultStatus();
        this.loadDashboardData();
    }

    setupEventListeners() {
        console.log("setupEventListeners: Starting event listener setup.");
        try {
            // Navigation
            document.querySelectorAll(".sidebar-menu .menu-item").forEach(item => {
                console.log("setupEventListeners: Attaching click listener to sidebar item:", item.dataset.page);
                item.addEventListener("click", (e) => {
                    e.preventDefault();
                    const page = e.currentTarget.dataset.page;
                    console.log("setupEventListeners: Sidebar item clicked, showing page:", page);
                    this.showPage(page);
                    document.querySelectorAll(".sidebar-menu .menu-item").forEach(el => el.classList.remove("active"));
                    e.currentTarget.classList.add("active");

                    // Close sidebar on mobile after click
                    const sidebar = document.querySelector(".sidebar");
                    if (sidebar && window.innerWidth <= 768) {
                        console.log("setupEventListeners: Closing sidebar on mobile.");
                        sidebar.classList.remove("active");
                    }
                });
            });

            // Hamburger menu toggle for mobile
            const menuToggleButton = document.querySelector(".menu-toggle-btn");
            if (menuToggleButton) {
                console.log("setupEventListeners: Attaching click listener to menu toggle button.");
                menuToggleButton.addEventListener("click", () => {
                    const sidebar = document.querySelector(".sidebar");
                    if (sidebar) {
                        console.log("setupEventListeners: Toggling sidebar visibility.");
                        sidebar.classList.toggle("active");
                    }
                });
            }

            // Power button with dual functionality
            const powerBtn = document.getElementById("powerBtn");
            if (powerBtn) {
                console.log("setupEventListeners: Attaching click listener to power button.");
                powerBtn.addEventListener("click", (event) => {
                    if (event.shiftKey) {
                        // Shift + Click = Power function (emergency stop)
                        if (confirm("هل أنت متأكد من إيقاف جميع الصفقات وإغلاق المراكز؟ هذا الإجراء لا رجعة فيه!")) {
                            this.showToast("تم إرسال طلب الإيقاف الفوري (تجريبي)", "error");
                            console.log("setupEventListeners: Emergency power stop confirmed.");
                        }
                    } else {
                        // Normal Click = Logout
                        this.handleLogout();
                    }
                });
            }

            // Logout button (top right)
            const logoutBtn = document.getElementById("logoutBtn");
            if (logoutBtn) {
                console.log("setupEventListeners: Attaching click listener to top logout button.");
                logoutBtn.addEventListener("click", () => this.handleLogout());
            }

            // Sidebar Logout button
            const sidebarLogoutBtn = document.getElementById("sidebarLogoutBtn");
            if (sidebarLogoutBtn) {
                console.log("setupEventListeners: Attaching click listener to sidebar logout button.");
                sidebarLogoutBtn.addEventListener("click", () => this.handleLogout());
            }

            // Vault status button
            const vaultStatusBtn = document.getElementById("vaultStatus");
            if (vaultStatusBtn) {
                console.log("setupEventListeners: Attaching click listener to vault status button.");
                vaultStatusBtn.addEventListener("click", () => this.toggleVault());
            }

            // Add Platform button
            const addPlatformBtn = document.getElementById("addPlatformBtn");
            if (addPlatformBtn) {
                console.log("setupEventListeners: Attaching click listener to add platform button.");
                addPlatformBtn.addEventListener("click", () => this.showToast("إضافة منصة (قيد التطوير)", "info"));
            }

            // Voice button
            const voiceBtn = document.getElementById("voiceBtn");
            if (voiceBtn) {
                console.log("setupEventListeners: Attaching click listener to voice button.");
                voiceBtn.addEventListener("click", () => this.showToast("المساعد الصوتي (قيد التطوير)", "info"));
            }

            // Refresh data button
            const refreshDataBtn = document.getElementById("refreshData");
            if (refreshDataBtn) {
                console.log("setupEventListeners: Attaching click listener to refresh data button.");
                refreshDataBtn.addEventListener("click", () => this.loadDashboardData());
            }

            // Toggle 2FA button
            const toggle2FABtn = document.getElementById("toggle2FA");
            if (toggle2FABtn) {
                console.log("setupEventListeners: Attaching click listener to toggle 2FA button.");
                toggle2FABtn.addEventListener("click", () => this.showToast("تفعيل/تعطيل المصادقة الثنائية (قيد التطوير)", "info"));
            }

            // Change password button
            const changePasswordBtn = document.getElementById("changePasswordBtn");
            if (changePasswordBtn) {
                console.log("setupEventListeners: Attaching click listener to change password button.");
                changePasswordBtn.addEventListener("click", () => this.showToast("تغيير كلمة المرور (قيد التطوير)", "info"));
            }
            console.log("setupEventListeners: All event listeners set up.");
        } catch (error) {
            console.error("setupEventListeners: Error during event listener setup:", error);
            this.showToast("خطأ في تهيئة الواجهة: " + error.message, "error");
        }
    }

    showPage(pageId) {
        console.log("showPage: Attempting to show page:", pageId);
        try {
            document.querySelectorAll(".page").forEach(page => {
                page.classList.remove("active");
            });
            const targetPage = document.getElementById(pageId + "Page");
            if (targetPage) {
                targetPage.classList.add("active");
                console.log("showPage: Page shown successfully:", pageId);
            } else {
                console.warn("showPage: Target page not found:", pageId + "Page");
                this.showToast("الصفحة المطلوبة غير موجودة: " + pageId, "warning");
            }
        } catch (error) {
            console.error("showPage: Error showing page:", error);
            this.showToast("خطأ في عرض الصفحة: " + error.message, "error");
        }
    }

    showMainApp() {
        console.log("showMainApp: Displaying main application.");
        try {
            document.getElementById("loginScreen").style.display = "none";
            document.getElementById("mainApp").style.display = "grid";
            this.showPage("home"); // Show home page by default
            console.log("showMainApp: Main app displayed, home page active.");
        } catch (error) {
            console.error("showMainApp: Error displaying main app:", error);
            this.showToast("خطأ في تحميل التطبيق الرئيسي: " + error.message, "error");
        }
    }

    updateUserInfo() {
        console.log("updateUserInfo: Updating user info.");
        try {
            const currentUserSpan = document.getElementById("currentUser");
            if (currentUserSpan) {
                currentUserSpan.textContent = "المستخدم التجريبي"; // Hardcoded for development
                console.log("updateUserInfo: User info updated.");
            }
        } catch (error) {
            console.error("updateUserInfo: Error updating user info:", error);
        }
    }

    checkVaultStatus() {
        console.log("checkVaultStatus: Checking vault status.");
        try {
            const vaultStatusBtn = document.getElementById("vaultStatus");
            if (vaultStatusBtn) {
                if (this.vaultUnlocked) {
                    vaultStatusBtn.innerHTML = `<i class="fas fa-lock-open"></i><span>الخزنة مفتوحة</span>`;
                    console.log("checkVaultStatus: Vault is unlocked.");
                } else {
                    vaultStatusBtn.innerHTML = `<i class="fas fa-lock"></i><span>الخزنة مقفولة</span>`;
                    console.log("checkVaultStatus: Vault is locked.");
                }
            }
        } catch (error) {
            console.error("checkVaultStatus: Error checking vault status:", error);
        }
    }

    toggleVault() {
        console.log("toggleVault: Toggling vault status.");
        try {
            this.vaultUnlocked = !this.vaultUnlocked;
            this.checkVaultStatus();
            this.showToast(this.vaultUnlocked ? "تم فتح الخزنة (تجريبي)" : "تم قفل الخزنة (تجريبي)", "info");
            console.log("toggleVault: Vault status toggled to:", this.vaultUnlocked);
        } catch (error) {
            console.error("toggleVault: Error toggling vault:", error);
        }
    }

    loadDashboardData() {
        console.log("loadDashboardData: Loading dashboard data.");
        try {
            // Simulate loading data
            document.getElementById("currentBalance").textContent = "$10,000.00";
            document.getElementById("unrealizedPnL").textContent = "+$0.00";
            document.getElementById("totalEquity").textContent = "$10,000.00";
            document.getElementById("openPositions").textContent = "0";
            document.getElementById("dailyPnL").querySelector(".pnl-value").textContent = "+$0.00 (0.00%)";
            document.getElementById("dailyPnL").querySelector(".pnl-value").classList.remove("negative");
            document.getElementById("dailyPnL").querySelector(".pnl-value").classList.add("positive");

            // Clear existing table data
            const positionsTableBody = document.getElementById("positionsTable").querySelector("tbody");
            positionsTableBody.innerHTML = `
                <tr class="no-data">
                    <td colspan="7">لا توجد مراكز مفتوحة</td>
                </tr>
            `;

            const ordersTableBody = document.getElementById("ordersTable").querySelector("tbody");
            ordersTableBody.innerHTML = `
                <tr class="no-data">
                    <td colspan="7">لا توجد أوامر معلقة</td>
                </tr>
            `;

            this.showToast("تم تحديث بيانات لوحة التحكم (تجريبي)", "success");
            this.renderPerformanceChart();
            console.log("loadDashboardData: Dashboard data loaded and chart rendered.");
        } catch (error) {
            console.error("loadDashboardData: Error loading dashboard data:", error);
            this.showToast("خطأ في تحميل بيانات لوحة التحكم: " + error.message, "error");
        }
    }

    renderPerformanceChart() {
        console.log("renderPerformanceChart: Rendering performance chart.");
        try {
            const ctx = document.getElementById("performanceChart").getContext("2d");
            if (this.performanceChart) {
                this.performanceChart.destroy();
            }
            this.performanceChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو"],
                    datasets: [{
                        label: "أداء المحفظة",
                        data: [0, 100, 150, 120, 200, 180, 250],
                        borderColor: "#6366f1",
                        backgroundColor: "rgba(99, 102, 241, 0.2)",
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)"
                            },
                            ticks: {
                                color: "#a1a1aa"
                            }
                        },
                        y: {
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)"
                            },
                            ticks: {
                                color: "#a1a1aa"
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: "#ffffff"
                            }
                        }
                    }
                }
            });
            console.log("renderPerformanceChart: Chart rendered successfully.");
        } catch (error) {
            console.error("renderPerformanceChart: Error rendering chart:", error);
            this.showToast("خطأ في رسم الرسم البياني: " + error.message, "error");
        }
    }

    handleLogout() {
        console.log("handleLogout: Logging out.");
        try {
            this.showToast("تم تسجيل الخروج (تجريبي)", "info");
            // In a real app, you would clear session data and redirect to login
            // For this simplified version, we just show a toast
            console.log("handleLogout: Logout toast shown.");
        } catch (error) {
            console.error("handleLogout: Error during logout:", error);
        }
    }

    showToast(message, type) {
        console.log(`showToast: Displaying toast - Type: ${type}, Message: ${message}`);
        try {
            const toastContainer = document.getElementById("toastContainer");
            if (!toastContainer) {
                console.warn("showToast: toastContainer not found.");
                return;
            }

            const toast = document.createElement("div");
            toast.classList.add("toast", type);
            toast.innerHTML = `<p>${message}</p>`;
            toastContainer.appendChild(toast);

            setTimeout(() => {
                console.log("showToast: Removing toast.");
                toast.remove();
            }, 3000);
            console.log("showToast: Toast displayed.");
        } catch (error) {
            console.error("showToast: Error displaying toast:", error);
        }
    }

    showMainApp() {
        document.getElementById("loginScreen").style.display = "none";
        document.getElementById("mainApp").style.display = "grid";
        this.showPage("home"); // Show home page by default
    }

    showPage(pageId) {
        document.querySelectorAll(".page").forEach(page => {
            page.classList.remove("active");
        });
        document.getElementById(pageId + "Page").classList.add("active");
    }

    updateUserInfo() {
        const currentUserSpan = document.getElementById("currentUser");
        if (currentUserSpan) {
            currentUserSpan.textContent = "المستخدم التجريبي"; // Hardcoded for development
        }
    }

    checkVaultStatus() {
        const vaultStatusBtn = document.getElementById("vaultStatus");
        if (vaultStatusBtn) {
            if (this.vaultUnlocked) {
                vaultStatusBtn.innerHTML = '<i class="fas fa-unlock"></i><span>الخزنة مفتوحة</span>';
            } else {
                vaultStatusBtn.innerHTML = '<i class="fas fa-lock"></i><span>الخزنة مقفولة</span>';
            }
        }
    }

    toggleVault() {
        this.vaultUnlocked = !this.vaultUnlocked;
        this.checkVaultStatus();
        this.showToast(this.vaultUnlocked ? "تم فتح الخزنة (تجريبي)" : "تم قفل الخزنة (تجريبي)", "info");
    }

    loadDashboardData() {
        // Simulate loading data
        document.getElementById("currentBalance").textContent = "$10,000.00";
        document.getElementById("unrealizedPnL").textContent = "+$0.00";
        document.getElementById("totalEquity").textContent = "$10,000.00";
        document.getElementById("openPositions").textContent = "0";
        document.getElementById("dailyPnL").querySelector(".pnl-value").textContent = "+$0.00 (0.00%)";
        document.getElementById("dailyPnL").querySelector(".pnl-value").classList.remove("negative");
        document.getElementById("dailyPnL").querySelector(".pnl-value").classList.add("positive");

        // Clear existing table data
        const positionsTableBody = document.getElementById("positionsTable").querySelector("tbody");
        positionsTableBody.innerHTML = '<tr><td colspan="6">لا توجد مراكز مفتوحة</td></tr>';

        const ordersTableBody = document.getElementById("ordersTable").querySelector("tbody");
        ordersTableBody.innerHTML = '<tr><td colspan="6">لا توجد أوامر معلقة</td></tr>';

        this.showToast("تم تحديث بيانات لوحة التحكم (تجريبي)", "success");
        this.renderPerformanceChart();
    }

    renderPerformanceChart() {
        const ctx = document.getElementById("performanceChart").getContext("2d");
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }
        this.performanceChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو"],
                datasets: [{
                    label: "أداء المحفظة",
                    data: [0, 100, 150, 120, 200, 180, 250],
                    borderColor: "#6366f1",
                    backgroundColor: "rgba(99, 102, 241, 0.2)",
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: {
                            color: "rgba(255, 255, 255, 0.1)"
                        },
                        ticks: {
                            color: "#a1a1aa"
                        }
                    },
                    y: {
                        grid: {
                            color: "rgba(255, 255, 255, 0.1)"
                        },
                        ticks: {
                            color: "#a1a1aa"
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: "#ffffff"
                        }
                    }
                }
            }
        });
    }

    handleLogout() {
        this.showToast("تم تسجيل الخروج (تجريبي)", "info");
        // In a real app, you would clear session data and redirect to login
        // For this simplified version, we just show a toast
    }
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOMContentLoaded: Initializing App.");
    new App();
});


