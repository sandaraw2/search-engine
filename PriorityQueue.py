import heapq
#
# class PriorityQueue:
#     def __init__(self):
#         self.pq = []  # The heap
#         self.entry_finder = {}  # Dictionary to track entries and their priorities
#         self.REMOVED = '<removed-task>'  # Placeholder for removed tasks
#         self.counter = 0  # Counter to handle tie-breaking
#
#     def add_task(self, task, priority=0):
#         """Add a new task or update the priority of an existing task."""
#         if task in self.entry_finder:
#             self.remove_task(task)
#         count = next(self.counter)
#         entry = [priority, count, task]
#         self.entry_finder[task] = entry
#         heapq.heappush(self.pq, entry)
#
#     def remove_task(self, task):
#         """Mark an existing task as REMOVED."""
#         entry = self.entry_finder.pop(task)
#         entry[-1] = self.REMOVED
#
#     def is_empty(self):
#         """Check if the priority queue is empty."""
#         return not bool(self.entry_finder)
#
# # Example usage:
# priority_queue = PriorityQueue()
#
# # Add tasks with priorities
# priority_queue.add_task('Task 1', 5)
# priority_queue.add_task('Task 2', 3)
# priority_queue.add_task('Task 3', 8)
#
# # Pop tasks in order of priority
# while not priority_queue.is_empty():
#     print(priority_queue.pop_task())
