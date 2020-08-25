
class LoopChecks:
  # TODO use DisjointSet instead

  def __init__(self):
    self._links = {}

  def __str__(self):
    return str({self._links})

  def create_loop(self, a, b):
    a_set = self._links.get(a)
    b_set = self._links.get(b)
    return a_set is b_set and a_set is not None

  def add(self, a, b):
    if self.create_loop(a, b):
      return False

    a_set = self._links.get(a)
    b_set = self._links.get(b)

    if a_set is None and b_set is None:
      ab_set = {a, b}
      self._links[a] = ab_set
      self._links[b] = ab_set
      return True

    if a_set is b_set:
      assert False

    if a_set is None:
      ab_set = self._links[b]
      ab_set.add(a)
      self._links[a] = ab_set
      return True

    if b_set is None:
      ab_set = self._links[a]
      ab_set.add(b)
      self._links[b] = ab_set
      return True

    # Worst case, need to add everything from a and b
    if b_set > a_set:
      b_set, a_set = a_set, b_set

    a_set.update(b_set)
    for e in b_set:
      self._links[e] = a_set
    return True
