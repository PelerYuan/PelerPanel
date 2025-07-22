/**
 * Peler Panel 主要JavaScript文件
 * 处理所有前端交互逻辑
 */

$(document).ready(function() {
    // 全局变量
    window.PelerPanel = {
        isAuthenticated: false,
        currentCards: [],
        currentIcons: {},
        sortableInstance: null,
        searchTimeout: null,
        currentEditingCard: null
    };

    // 初始化应用
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    // 检查认证状态
    checkAuthStatus();

    // 加载卡片
    loadCards();

    // 绑定事件处理器
    bindEventHandlers();

    // 初始化组件
    initializeComponents();
}

/**
 * 检查认证状态
 */
function checkAuthStatus() {
    $.get('/api/auth/status')
        .done(function(response) {
            if (response.success) {
                window.PelerPanel.isAuthenticated = response.data.authenticated;
                updateAuthUI();
            }
        })
        .fail(function() {
            window.PelerPanel.isAuthenticated = false;
            updateAuthUI();
        });
}

/**
 * 更新认证相关UI
 */
function updateAuthUI() {
    // 这里可以根据认证状态更新UI元素
    // 例如显示/隐藏管理按钮等
}

/**
 * 加载卡片数据
 */
function loadCards(searchQuery = '') {
    showLoading();

    const params = {};
    if (searchQuery) {
        params.search = searchQuery;
    }

    $.get('/api/cards', params)
        .done(function(response) {
            if (response.success) {
                window.PelerPanel.currentCards = response.data.items || [];
                renderCards();
                updateCardStats();
            } else {
                showToast('加载失败', response.message, 'danger');
            }
        })
        .fail(function(xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '加载卡片失败';
            showToast('网络错误', errorMsg, 'danger');
            window.PelerPanel.currentCards = [];
            renderCards();
        })
        .always(function() {
            hideLoading();
        });
}

/**
 * 渲染卡片
 */
function renderCards() {
    const cards = window.PelerPanel.currentCards;
    const searchQuery = $('#searchInput').val().toLowerCase();

    if (cards.length === 0) {
        showEmptyState(searchQuery);
        return;
    }

    hideEmptyState();

    // 根据视图模式渲染
    const viewMode = $('input[name="viewMode"]:checked').attr('id');
    if (viewMode === 'listView') {
        renderListView(cards, searchQuery);
    } else {
        renderGridView(cards, searchQuery);
    }

    // 初始化拖拽排序（仅网格视图且已认证）
    if (viewMode === 'gridView' && window.PelerPanel.isAuthenticated) {
        initializeSortable();
    }
}

/**
 * 渲染网格视图
 */
function renderGridView(cards, searchQuery) {
    $('#cardsList').addClass('d-none');
    $('#cardsGrid').removeClass('d-none');

    const $grid = $('#cardsGrid');
    $grid.empty();

    cards.forEach(function(card) {
        const cardHtml = createCardHtml(card, searchQuery);
        $grid.append(cardHtml);
    });

    // 添加动画效果
    $('#cardsGrid .service-card').addClass('fade-in');
}

/**
 * 渲染列表视图
 */
function renderListView(cards, searchQuery) {
    $('#cardsGrid').addClass('d-none');
    $('#cardsList').removeClass('d-none');

    const $tbody = $('#cardsTableBody');
    $tbody.empty();

    cards.forEach(function(card) {
        const rowHtml = createTableRowHtml(card, searchQuery);
        $tbody.append(rowHtml);
    });
}

/**
 * 创建卡片HTML
 */
function createCardHtml(card, searchQuery = '') {
    const highlightedName = highlightSearchTerm(card.name, searchQuery);
    const highlightedDesc = highlightSearchTerm(card.description, searchQuery);

    return `
        <div class="col-xl-3 col-lg-4 col-md-6 col-sm-12" data-card-id="${card.id}">
            <div class="card service-card shadow-sm h-100" onclick="openService('${card.url}')">
                <div class="card-body d-flex flex-column">
                    ${window.PelerPanel.isAuthenticated ? `
                    <div class="admin-controls">
                        <button class="btn btn-sm btn-outline-primary" onclick="editCard(event, '${card.id}')" 
                                title="编辑">
                            <i class="bi bi-pencil"></i>
                        </button>
                    </div>
                    ` : ''}
                    
                    <div class="text-center mb-3">
                        <i class="service-icon ${card.icon}"></i>
                    </div>
                    
                    <h6 class="service-name text-center">${highlightedName}</h6>
                    
                    <p class="service-description text-center flex-grow-1">
                        ${highlightedDesc}
                    </p>
                    
                    <small class="service-url text-center">
                        ${card.url}
                    </small>
                </div>
                
                ${window.PelerPanel.isAuthenticated ? `
                <div class="drag-hint">
                    <i class="bi bi-grip-horizontal"></i> 拖拽排序
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

/**
 * 创建表格行HTML
 */
function createTableRowHtml(card, searchQuery = '') {
    const highlightedName = highlightSearchTerm(card.name, searchQuery);
    const highlightedDesc = highlightSearchTerm(card.description, searchQuery);

    return `
        <tr data-card-id="${card.id}">
            <td class="text-center">
                <i class="service-icon-sm ${card.icon}"></i>
            </td>
            <td>
                <strong>${highlightedName}</strong>
            </td>
            <td>${highlightedDesc}</td>
            <td>
                <a href="${card.url}" target="_blank" rel="noopener noreferrer" 
                   class="text-decoration-none" onclick="event.stopPropagation()">
                    ${card.url}
                    <i class="bi bi-box-arrow-up-right ms-1"></i>
                </a>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="openService('${card.url}')" title="访问">
                        <i class="bi bi-box-arrow-up-right"></i>
                    </button>
                    ${window.PelerPanel.isAuthenticated ? `
                    <button class="btn btn-outline-secondary" onclick="editCard(event, '${card.id}')" title="编辑">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

/**
 * 高亮搜索词
 */
function highlightSearchTerm(text, searchQuery) {
    if (!searchQuery || !text) return text;

    const regex = new RegExp(`(${escapeRegExp(searchQuery)})`, 'gi');
    return text.replace(regex, '<span class="search-highlight">$1</span>');
}

/**
 * 转义正则表达式特殊字符
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * 显示空状态
 */
function showEmptyState(hasSearchQuery) {
    $('#cardsGrid, #cardsList').addClass('d-none');

    if (hasSearchQuery) {
        $('#emptyState').addClass('d-none');
        $('#noSearchResults').removeClass('d-none');
    } else {
        $('#noSearchResults').addClass('d-none');
        $('#emptyState').removeClass('d-none');
    }
}

/**
 * 隐藏空状态
 */
function hideEmptyState() {
    $('#emptyState, #noSearchResults').addClass('d-none');
}

/**
 * 更新卡片统计信息
 */
function updateCardStats() {
    const total = window.PelerPanel.currentCards.length;
    const searchQuery = $('#searchInput').val();

    if (searchQuery) {
        // 可以在这里显示搜索结果统计
    }

    // 更新标题或其他统计显示
    document.title = `Peler Panel - ${total}个服务`;
}

/**
 * 初始化拖拽排序
 */
function initializeSortable() {
    if (window.PelerPanel.sortableInstance) {
        window.PelerPanel.sortableInstance.destroy();
    }

    const gridElement = document.getElementById('cardsGrid');
    if (!gridElement) return;

    window.PelerPanel.sortableInstance = Sortable.create(gridElement, {
        animation: 200,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        onEnd: function(evt) {
            if (evt.oldIndex !== evt.newIndex) {
                updateCardOrder();
            }
        }
    });
}

/**
 * 更新卡片排序
 */
function updateCardOrder() {
    const cardElements = $('#cardsGrid > div[data-card-id]');
    const orders = [];

    cardElements.each(function(index, element) {
        const cardId = $(element).data('card-id');
        orders.push({
            id: cardId,
            order: index + 1
        });
    });

    $.ajax({
        url: '/api/cards/reorder',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ orders: orders }),
        success: function(response) {
            if (response.success) {
                showToast('排序成功', '卡片排序已更新', 'success');
                // 更新本地数据
                orders.forEach(function(item) {
                    const card = window.PelerPanel.currentCards.find(c => c.id === item.id);
                    if (card) {
                        card.order = item.order;
                    }
                });
            } else {
                showToast('排序失败', response.message, 'danger');
                loadCards(); // 重新加载以恢复原序
            }
        },
        error: function() {
            showToast('排序失败', '网络错误', 'danger');
            loadCards(); // 重新加载以恢复原序
        }
    });
}

/**
 * 绑定事件处理器
 */
function bindEventHandlers() {
    // 搜索功能
    $('#searchInput').on('input', function() {
        clearTimeout(window.PelerPanel.searchTimeout);
        const query = $(this).val();

        window.PelerPanel.searchTimeout = setTimeout(function() {
            loadCards(query);
        }, 300);
    });

    // 清除搜索
    $('#clearSearch').on('click', function() {
        $('#searchInput').val('');
        loadCards();
    });

    // 视图模式切换
    $('input[name="viewMode"]').on('change', function() {
        renderCards();
    });

    // 刷新按钮
    $('#refreshCards').on('click', function() {
        loadCards($('#searchInput').val());
    });

    // 添加卡片按钮
    $('#addCardBtn').on('click', function() {
        showAddCardModal();
    });

    // 认证表单
    $('#authForm').on('submit', function(e) {
        e.preventDefault();
        performAuthentication();
    });

    // 密码显示切换
    $('#togglePassword').on('click', function() {
        const input = $('#adminPassword');
        const icon = $(this).find('i');

        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            icon.removeClass('bi-eye').addClass('bi-eye-slash');
        } else {
            input.attr('type', 'password');
            icon.removeClass('bi-eye-slash').addClass('bi-eye');
        }
    });

    // 卡片编辑表单
    $('#cardForm').on('submit', function(e) {
        e.preventDefault();
        submitCardForm();
    });

    // 描述字符统计
    $('#cardDescription').on('input', function() {
        const count = $(this).val().length;
        $('#descriptionCount').text(count);

        if (count > 200) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });

    // 图标选择
    $('#selectIconBtn').on('click', function() {
        showIconModal();
    });

    // 图标搜索
    $('#iconSearch').on('input', function() {
        const query = $(this).val();
        filterIcons(query);
    });

    // 确认选择图标
    $('#confirmIconBtn').on('click', function() {
        confirmIconSelection();
    });

    // 删除卡片
    $('#deleteCardBtn').on('click', function() {
        showDeleteConfirmModal();
    });

    // 确认删除
    $('#confirmDeleteBtn').on('click', function() {
        deleteCurrentCard();
    });

    // 模态框事件
    $('#cardModal').on('hidden.bs.modal', function() {
        resetCardForm();
    });

    $('#authModal').on('hidden.bs.modal', function() {
        resetAuthForm();
    });
}

/**
 * 初始化组件
 */
function initializeComponents() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 设置初始视图模式
    $('#gridView').prop('checked', true);
}

/**
 * 打开服务链接
 */
function openService(url) {
    window.open(url, '_blank', 'noopener,noreferrer');
}

/**
 * 显示添加卡片模态框
 */
function showAddCardModal() {
    if (!window.PelerPanel.isAuthenticated) {
        showAuthModal('add_card');
        return;
    }

    window.PelerPanel.currentEditingCard = null;
    $('#cardModalTitle').html('<i class="bi bi-plus-circle me-2"></i>添加服务');
    $('#cardSubmitText').text('添加');
    $('#deleteCardBtn').hide();

    const modal = new bootstrap.Modal('#cardModal');
    modal.show();
}

/**
 * 编辑卡片
 */
function editCard(event, cardId) {
    event.stopPropagation();

    if (!window.PelerPanel.isAuthenticated) {
        showAuthModal('edit_card', cardId);
        return;
    }

    const card = window.PelerPanel.currentCards.find(c => c.id === cardId);
    if (!card) {
        showToast('错误', '卡片不存在', 'danger');
        return;
    }

    window.PelerPanel.currentEditingCard = card;

    // 填充表单
    $('#cardName').val(card.name);
    $('#cardIcon').val(card.icon);
    $('#cardUrl').val(card.url);
    $('#cardDescription').val(card.description || '');
    $('#descriptionCount').text((card.description || '').length);

    // 更新图标预览
    updateIconPreview(card.icon);

    // 更新模态框标题
    $('#cardModalTitle').html('<i class="bi bi-pencil me-2"></i>编辑服务');
    $('#cardSubmitText').text('保存');
    $('#deleteCardBtn').show();

    const modal = new bootstrap.Modal('#cardModal');
    modal.show();
}

/**
 * 显示认证模态框
 */
function showAuthModal(action, cardId = null) {
    window.PelerPanel.pendingAction = { action, cardId };

    const modal = new bootstrap.Modal('#authModal', {
        backdrop: 'static',
        keyboard: false
    });
    modal.show();

    // 聚焦密码输入框
    $('#authModal').on('shown.bs.modal', function() {
        $('#adminPassword').focus();
    });
}

/**
 * 执行认证
 */
function performAuthentication() {
    const password = $('#adminPassword').val();

    if (!password) {
        $('#adminPassword').addClass('is-invalid');
        $('#passwordError').text('请输入密码');
        return;
    }

    $('#authSpinner').removeClass('d-none');
    $('#adminPassword').prop('disabled', true);

    $.ajax({
        url: '/api/auth',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ password: password }),
        success: function(response) {
            if (response.success) {
                window.PelerPanel.isAuthenticated = true;
                updateAuthUI();

                // 关闭认证模态框
                bootstrap.Modal.getInstance('#authModal').hide();

                // 执行待处理的操作
                executeAuthAction();

                showToast('认证成功', '管理员登录成功', 'success');
            } else {
                handleAuthError(response);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON || {};
            handleAuthError(response);
        },
        complete: function() {
            $('#authSpinner').addClass('d-none');
            $('#adminPassword').prop('disabled', false);
        }
    });
}

/**
 * 处理认证错误
 */
function handleAuthError(response) {
    $('#adminPassword').addClass('is-invalid').val('');
    $('#passwordError').text(response.message || '认证失败');

    // 显示安全信息
    if (response.details) {
        let securityMsg = '';
        if (response.details.attempts_left) {
            securityMsg = `还有 ${response.details.attempts_left} 次尝试机会`;
        } else if (response.details.locked) {
            securityMsg = '账户已被锁定，请稍后重试';
        }

        if (securityMsg) {
            $('#securityMessage').text(securityMsg);
            $('#securityInfo').removeClass('d-none');
        }
    }

    // 重新聚焦
    setTimeout(() => $('#adminPassword').focus(), 100);
}

/**
 * 执行认证后的操作
 */
function executeAuthAction() {
    const action = window.PelerPanel.pendingAction;
    if (!action) return;

    switch (action.action) {
        case 'add_card':
            showAddCardModal();
            break;
        case 'edit_card':
            editCard({ stopPropagation: () => {} }, action.cardId);
            break;
    }

    delete window.PelerPanel.pendingAction;
}

/**
 * 重置认证表单
 */
function resetAuthForm() {
    $('#adminPassword').val('').removeClass('is-invalid').prop('disabled', false);
    $('#passwordError').text('');
    $('#securityInfo').addClass('d-none');
    $('#authSpinner').addClass('d-none');
}

/**
 * 提交卡片表单
 */
function submitCardForm() {
    if (!validateCardForm()) return;

    const formData = {
        name: $('#cardName').val().trim(),
        icon: $('#cardIcon').val().trim(),
        url: $('#cardUrl').val().trim(),
        description: $('#cardDescription').val().trim()
    };

    $('#cardSpinner').removeClass('d-none');

    const isEditing = window.PelerPanel.currentEditingCard !== null;
    const url = isEditing ? `/api/cards/${window.PelerPanel.currentEditingCard.id}` : '/api/cards';
    const method = isEditing ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        type: method,
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                bootstrap.Modal.getInstance('#cardModal').hide();
                loadCards($('#searchInput').val());

                const action = isEditing ? '更新' : '添加';
                showToast(`${action}成功`, `服务已${action}`, 'success');
            } else {
                showToast(`${isEditing ? '更新' : '添加'}失败`, response.message, 'danger');
            }
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '操作失败';
            showToast('网络错误', errorMsg, 'danger');
        },
        complete: function() {
            $('#cardSpinner').addClass('d-none');
        }
    });
}

/**
 * 验证卡片表单
 */
function validateCardForm() {
    let isValid = true;

    // 验证名称
    const name = $('#cardName').val().trim();
    if (!name) {
        $('#cardName').addClass('is-invalid');
        $('#cardName').siblings('.invalid-feedback').text('请输入服务名称');
        isValid = false;
    } else if (name.length > 50) {
        $('#cardName').addClass('is-invalid');
        $('#cardName').siblings('.invalid-feedback').text('名称不能超过50个字符');
        isValid = false;
    } else {
        $('#cardName').removeClass('is-invalid').addClass('is-valid');
    }

    // 验证图标
    const icon = $('#cardIcon').val().trim();
    if (!icon) {
        $('#cardIcon').addClass('is-invalid');
        $('#cardIcon').siblings('.invalid-feedback').text('请选择图标');
        isValid = false;
    } else {
        $('#cardIcon').removeClass('is-invalid').addClass('is-valid');
    }

    // 验证URL
    const url = $('#cardUrl').val().trim();
    if (!url) {
        $('#cardUrl').addClass('is-invalid');
        $('#cardUrl').siblings('.invalid-feedback').text('请输入访问链接');
        isValid = false;
    } else if (!isValidUrl(url)) {
        $('#cardUrl').addClass('is-invalid');
        $('#cardUrl').siblings('.invalid-feedback').text('请输入有效的URL地址');
        isValid = false;
    } else {
        $('#cardUrl').removeClass('is-invalid').addClass('is-valid');
    }

    // 验证描述长度
    const description = $('#cardDescription').val();
    if (description.length > 200) {
        $('#cardDescription').addClass('is-invalid');
        isValid = false;
    } else {
        $('#cardDescription').removeClass('is-invalid');
    }

    return isValid;
}

/**
 * 验证URL格式
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * 重置卡片表单
 */
function resetCardForm() {
    $('#cardForm')[0].reset();
    $('#cardForm .form-control').removeClass('is-valid is-invalid');
    $('#descriptionCount').text('0');
    updateIconPreview('');
    window.PelerPanel.currentEditingCard = null;
}

/**
 * 显示图标选择模态框
 */
function showIconModal() {
    loadIcons();
    const modal = new bootstrap.Modal('#iconModal');
    modal.show();
}

/**
 * 加载图标
 */
function loadIcons() {
    if (Object.keys(window.PelerPanel.currentIcons).length > 0) {
        renderIcons();
        return;
    }

    $.get('/api/icons')
        .done(function(response) {
            if (response.success) {
                window.PelerPanel.currentIcons = response.data.categories;
                renderIcons();
                renderIconCategories();
            } else {
                showToast('加载失败', '无法加载图标列表', 'danger');
            }
        })
        .fail(function() {
            showToast('网络错误', '无法加载图标列表', 'danger');
        });
}

/**
 * 渲染图标分类
 */
function renderIconCategories() {
    const $categories = $('#iconCategories');
    $categories.empty();

    // 添加"全部"分类
    $categories.append(`
        <button class="category-tag active" data-category="">
            全部
        </button>
    `);

    // 添加各个分类
    Object.keys(window.PelerPanel.currentIcons).forEach(function(category) {
        const categoryName = getCategoryDisplayName(category);
        $categories.append(`
            <button class="category-tag" data-category="${category}">
                ${categoryName}
            </button>
        `);
    });

    // 绑定分类点击事件
    $('.category-tag').on('click', function() {
        $('.category-tag').removeClass('active');
        $(this).addClass('active');

        const category = $(this).data('category');
        filterIconsByCategory(category);
    });
}

/**
 * 获取分类显示名称
 */
function getCategoryDisplayName(category) {
    const categoryNames = {
        'system': '系统',
        'monitoring': '监控',
        'storage': '存储',
        'development': '开发',
        'network': '网络',
        'security': '安全',
        'media': '媒体',
        'communication': '通讯',
        'general': '通用'
    };

    return categoryNames[category] || category;
}

/**
 * 渲染图标
 */
function renderIcons(iconsData = null) {
    const $grid = $('#iconGrid');
    $grid.empty();

    const icons = iconsData || window.PelerPanel.currentIcons;

    Object.keys(icons).forEach(function(category) {
        icons[category].forEach(function(icon) {
            const $iconItem = $(`
                <div class="icon-item" data-icon="${icon.name}" title="${icon.description}">
                    <i class="${icon.name}"></i>
                    <small>${icon.description}</small>
                </div>
            `);

            $iconItem.on('click', function() {
                selectIcon(icon.name);
            });

            $grid.append($iconItem);
        });
    });
}

/**
 * 按分类过滤图标
 */
function filterIconsByCategory(category) {
    if (!category) {
        renderIcons();
        return;
    }

    const filteredIcons = {};
    filteredIcons[category] = window.PelerPanel.currentIcons[category];
    renderIcons(filteredIcons);
}

/**
 * 过滤图标
 */
function filterIcons(query) {
    if (!query) {
        renderIcons();
        return;
    }

    const filtered = {};
    query = query.toLowerCase();

    Object.keys(window.PelerPanel.currentIcons).forEach(function(category) {
        const categoryIcons = window.PelerPanel.currentIcons[category].filter(function(icon) {
            return icon.name.toLowerCase().includes(query) ||
                   icon.description.toLowerCase().includes(query);
        });

        if (categoryIcons.length > 0) {
            filtered[category] = categoryIcons;
        }
    });

    renderIcons(filtered);
}

/**
 * 选择图标
 */
function selectIcon(iconName) {
    $('.icon-item').removeClass('selected');
    $(`.icon-item[data-icon="${iconName}"]`).addClass('selected');
    $('#confirmIconBtn').prop('disabled', false);

    window.PelerPanel.selectedIcon = iconName;
}

/**
 * 确认图标选择
 */
function confirmIconSelection() {
    if (!window.PelerPanel.selectedIcon) return;

    $('#cardIcon').val(window.PelerPanel.selectedIcon);
    updateIconPreview(window.PelerPanel.selectedIcon);

    bootstrap.Modal.getInstance('#iconModal').hide();

    // 重置选择状态
    $('#confirmIconBtn').prop('disabled', true);
    delete window.PelerPanel.selectedIcon;
}

/**
 * 更新图标预览
 */
function updateIconPreview(iconName) {
    const $preview = $('#iconPreview');

    if (iconName) {
        $preview.removeClass().addClass(`bi ${iconName} display-4 text-primary`);
    } else {
        $preview.removeClass().addClass('bi bi-question-circle display-4 text-muted');
    }
}

/**
 * 显示删除确认模态框
 */
function showDeleteConfirmModal() {
    if (!window.PelerPanel.currentEditingCard) return;

    $('#deleteCardName').text(window.PelerPanel.currentEditingCard.name);

    const modal = new bootstrap.Modal('#deleteConfirmModal');
    modal.show();
}

/**
 * 删除当前卡片
 */
function deleteCurrentCard() {
    if (!window.PelerPanel.currentEditingCard) return;

    const cardId = window.PelerPanel.currentEditingCard.id;
    const cardName = window.PelerPanel.currentEditingCard.name;

    $('#deleteSpinner').removeClass('d-none');
    $('#confirmDeleteBtn').prop('disabled', true);

    $.ajax({
        url: `/api/cards/${cardId}`,
        type: 'DELETE',
        success: function(response) {
            if (response.success) {
                bootstrap.Modal.getInstance('#deleteConfirmModal').hide();
                bootstrap.Modal.getInstance('#cardModal').hide();

                loadCards($('#searchInput').val());
                showToast('删除成功', `服务 "${cardName}" 已删除`, 'success');
            } else {
                showToast('删除失败', response.message, 'danger');
            }
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '删除失败';
            showToast('网络错误', errorMsg, 'danger');
        },
        complete: function() {
            $('#deleteSpinner').addClass('d-none');
            $('#confirmDeleteBtn').prop('disabled', false);
        }
    });
}

/**
 * 清除搜索
 */
function clearSearch() {
    $('#searchInput').val('');
    loadCards();
}

/**
 * 显示加载状态
 */
function showLoading() {
    $('#loadingOverlay').removeClass('d-none');
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    $('#loadingOverlay').addClass('d-none');
}

/**
 * 显示Toast通知
 */
function showToast(title, message, type = 'info') {
    const iconMap = {
        'success': 'bi-check-circle text-success',
        'danger': 'bi-exclamation-circle text-danger',
        'warning': 'bi-exclamation-triangle text-warning',
        'info': 'bi-info-circle text-primary'
    };

    $('#toastIcon').removeClass().addClass(`bi ${iconMap[type] || iconMap.info} me-2`);
    $('#toastTitle').text(title);
    $('#toastMessage').text(message);

    const toast = new bootstrap.Toast('#toastNotification', {
        autohide: true,
        delay: type === 'danger' ? 5000 : 3000
    });

    toast.show();
}

/**
 * 实用工具函数
 */

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 格式化时间
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minute = 60 * 1000;
    const hour = minute * 60;
    const day = hour * 24;

    if (diff < minute) {
        return '刚刚';
    } else if (diff < hour) {
        return Math.floor(diff / minute) + '分钟前';
    } else if (diff < day) {
        return Math.floor(diff / hour) + '小时前';
    } else if (diff < day * 30) {
        return Math.floor(diff / day) + '天前';
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('复制成功', '链接已复制到剪贴板', 'success');
        }).catch(function(err) {
            console.error('复制失败:', err);
            showToast('复制失败', '无法复制到剪贴板', 'danger');
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showToast('复制成功', '链接已复制到剪贴板', 'success');
        } catch (err) {
            console.error('复制失败:', err);
            showToast('复制失败', '无法复制到剪贴板', 'danger');
        }

        document.body.removeChild(textArea);
    }
}

// 全屏功能
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.error('无法进入全屏模式:', err);
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        $('#searchInput').focus();
    }

    // Ctrl/Cmd + N: 添加新卡片 (仅在已认证时)
    if ((e.ctrlKey || e.metaKey) && e.key === 'n' && window.PelerPanel.isAuthenticated) {
        e.preventDefault();
        showAddCardModal();
    }

    // Ctrl/Cmd + R: 刷新卡片
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        loadCards($('#searchInput').val());
    }

    // ESC: 清除搜索
    if (e.key === 'Escape' && $('#searchInput').val()) {
        clearSearch();
    }
});

// 监听网络状态
window.addEventListener('online', function() {
    showToast('网络已连接', '网络连接已恢复', 'success');
    loadCards($('#searchInput').val());
});

window.addEventListener('offline', function() {
    showToast('网络已断开', '请检查网络连接', 'warning');
});

// 页面可见性变化时刷新数据
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // 页面变为可见时，检查认证状态并刷新数据
        checkAuthStatus();
        loadCards($('#searchInput').val());
    }
});

// 导出全局函数供HTML调用
window.openService = openService;
window.editCard = editCard;
window.showAddCardModal = showAddCardModal;
window.clearSearch = clearSearch;
window.copyToClipboard = copyToClipboard;