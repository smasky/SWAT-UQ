document.addEventListener("DOMContentLoaded", function () {
  const tocLinks = document.querySelectorAll(".md-sidebar--secondary nav.md-nav a");
  const nestedLists = document.querySelectorAll(".md-sidebar--secondary nav.md-nav ul ul");
  let lastExpandedId = ""; // 记录上次展开的ID，避免重复操作
  let isProcessing = false; // 防止并发处理

  // 预先构建链接到ID的映射，提高查找效率
  const linkToIdMap = new Map();
  tocLinks.forEach(link => {
    const href = link.getAttribute("href");
    if (href && href.startsWith("#")) {
      linkToIdMap.set(href.substring(1), link);
    }
  });

  function collapseAll() {
    nestedLists.forEach(ul => ul.classList.remove("expanded"));
    tocLinks.forEach(link => link.classList.remove("open"));
  }

  function expandMatchingToc(id) {
    if (!id || id === lastExpandedId) return false; // 如果ID没变，不执行任何操作
    lastExpandedId = id;
    
    const link = linkToIdMap.get(id);
    if (!link) return false;
    
    const parentLi = link.closest("li");
    if (!parentLi) return false;
    
    // 先展开父级目录
    let parent = parentLi.parentElement;
    while (parent && parent.tagName === "UL") {
      parent.classList.add("expanded");
      const parentLink = parent.parentElement.querySelector("a");
      if (parentLink) parentLink.classList.add("open");
      parent = parent.parentElement.parentElement;
    }
    
    // 再展开子目录
    const childUl = parentLi.querySelector("ul");
    if (childUl) {
      childUl.classList.add("expanded");
      link.classList.add("open");
    }
    
    // 高亮当前链接
    link.classList.add("open");
    
    return true;
  }

  // 获取当前视图中最合适的标题ID
  function getCurrentSectionId() {
    const headings = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
    if (!headings.length) return "";
    
    // 使用视窗高度的1/4位置作为参考点
    const viewportHeight = window.innerHeight;
    const referencePoint = Math.min(200, viewportHeight / 4);
    
    // 第一阶段：优先查找接近参考点的标题
    let closestHeading = null;
    let minDistance = Infinity;
    
    for (const heading of headings) {
      const rect = heading.getBoundingClientRect();
      // 只考虑已经进入视窗的标题
      if (rect.top >= 0) {
        const distance = Math.abs(rect.top - referencePoint);
        if (distance < minDistance) {
          minDistance = distance;
          closestHeading = heading;
        }
      }
    }
    
    // 如果视窗内没有找到合适的标题，则找最接近顶部的标题
    if (!closestHeading) {
      for (const heading of headings) {
        const rect = heading.getBoundingClientRect();
        if (rect.top >= 0 && (closestHeading === null || rect.top < closestHeading.getBoundingClientRect().top)) {
          closestHeading = heading;
        }
      }
    }
    
    return closestHeading ? closestHeading.id : "";
  }
  
  // 处理滚动事件的主函数
  function updateTOC() {
    if (isProcessing) return;
    isProcessing = true;
    
    try {
      const id = getCurrentSectionId();
      if (id) {
        // 仅在ID变化时才执行折叠和展开操作
        if (id !== lastExpandedId) {
          collapseAll();
          expandMatchingToc(id);
        }
      }
    } finally {
      isProcessing = false;
    }
  }

  // 使用requestAnimationFrame进行滚动处理
  let scrollHandler = null;
  window.addEventListener("scroll", function() {
    // 取消之前的滚动处理
    if (scrollHandler) {
      cancelAnimationFrame(scrollHandler);
    }
    
    // 注册新的滚动处理
    scrollHandler = requestAnimationFrame(function() {
      scrollHandler = null;
      updateTOC();
    });
  }, { passive: true });
  
  // 延迟初始化以确保页面完全加载
  setTimeout(function() {
    updateTOC();
    // 确保在窗口大小变化时也更新TOC
    window.addEventListener("resize", updateTOC, { passive: true });
  }, 500);
});
