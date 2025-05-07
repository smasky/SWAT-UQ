document.addEventListener("DOMContentLoaded", function() {
    // Select all third-level headers in the TOC
    var tocItems = document.querySelectorAll('.md-nav__item--level-3');

    tocItems.forEach(function(item) {
        // Initially hide the third-level items
        item.style.display = 'none';

        // Add a click event to the parent item to toggle visibility
        var parent = item.parentElement.querySelector('.md-nav__link');
        if (parent) {
            parent.addEventListener('click', function() {
                item.style.display = item.style.display === 'none' ? 'block' : 'none';
            });
        }
    });
});