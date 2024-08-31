class Pagination:
    def __init__(self, total, page, per_page, items):
        self.total = total
        self.page = page
        self.per_page = per_page
        self.items = items
        self.has_prev = page > 1
        self.pages = (total + per_page - 1) // per_page  
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

    def iter_pages(self, left=2, right=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left or (num > self.pages - right and num <= self.pages):
                if last + 1 != num:
                    yield None
                yield num
                last = num