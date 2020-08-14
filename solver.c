/*
 * Solver. Returns 0 for impossibility, 1 for success, 2 for
 * ambiguity or failure to converge.
 */
static int slant_solve(int w, int h, const signed char *clues,
		       signed char *soln, struct solver_scratch *sc,
		       int difficulty)
{
    int W = w+1, H = h+1;
    int x, y, i, j;
    bool done_something;

    /*
     * Clear the output.
     */
    memset(soln, 0, w*h);

    sc->clues = clues;

    /*
     * Establish a disjoint set forest for tracking connectedness
     * between grid points.
     */
    dsf_init(sc->connected, W*H);

    /*
     * Establish a disjoint set forest for tracking which squares
     * are known to slant in the same direction.
     */
    dsf_init(sc->equiv, w*h);

    /*
     * Clear the slashval array.
     */
    memset(sc->slashval, 0, w*h);

    /*
     * Repeatedly try to deduce something until we can't.
     */
    do {
      done_something = false;

	/*
	 * Any clue point with the number of remaining lines equal
	 * to zero or to the number of remaining undecided
	 * neighbouring squares can be filled in completely.
	 */
	for (y = 0; y < H; y++)
	    for (x = 0; x < W; x++) {
		struct {
		    int pos, slash;
		} neighbours[4];
		int nneighbours;
		int nu, nl, c, s, eq, eq2, last, meq, mj1, mj2;

		if ((c = clues[y*W+x]) < 0)
		    continue;

		/*
		 * We have a clue point. Start by listing its
		 * neighbouring squares, in order around the point,
		 * together with the type of slash that would be
		 * required in that square to connect to the point.
		 */
		nneighbours = 0;
		if (x > 0 && y > 0) {
		    neighbours[nneighbours].pos = (y-1)*w+(x-1);
		    neighbours[nneighbours].slash = -1;
		    nneighbours++;
		}
		if (x > 0 && y < h) {
		    neighbours[nneighbours].pos = y*w+(x-1);
		    neighbours[nneighbours].slash = +1;
		    nneighbours++;
		}
		if (x < w && y < h) {
		    neighbours[nneighbours].pos = y*w+x;
		    neighbours[nneighbours].slash = -1;
		    nneighbours++;
		}
		if (x < w && y > 0) {
		    neighbours[nneighbours].pos = (y-1)*w+x;
		    neighbours[nneighbours].slash = +1;
		    nneighbours++;
		}

		/*
		 * Count up the number of undecided neighbours, and
		 * also the number of lines already present.
		 *
		 * If we're not on DIFF_EASY, then in this loop we
		 * also track whether we've seen two adjacent empty
		 * squares belonging to the same equivalence class
		 * (meaning they have the same type of slash). If
		 * so, we count them jointly as one line.
		 */
		nu = 0;
		nl = c;
		last = neighbours[nneighbours-1].pos;
		if (soln[last] == 0)
		    eq = dsf_canonify(sc->equiv, last);
		else
		    eq = -1;
		meq = mj1 = mj2 = -1;
		for (i = 0; i < nneighbours; i++) {
		    j = neighbours[i].pos;
		    s = neighbours[i].slash;
		    if (soln[j] == 0) {
			nu++;	       /* undecided */

			eq = -1;
			if (soln[j] == s)
			    nl--;      /* here's a line */
		    }
		    last = j;

		/*
		 * Check the counts.
		 */
		if (nl < 0 || nl > nu) {
		    /*
		     * No consistent value for this at all!
		     */
		    return 0;	       /* impossible */
		}

		if (nu > 0 && (nl == 0 || nl == nu)) {
		    for (i = 0; i < nneighbours; i++) {
			j = neighbours[i].pos;
			s = neighbours[i].slash;
			if (soln[j] == 0 && j != mj1 && j != mj2)
			    fill_square(w, h, j%w, j/w, (nl ? s : -s), soln,
					sc->connected, sc);
		    }

		    done_something = true;
		} else if (nu == 2 && nl == 1 && difficulty > DIFF_EASY) {
		    /*
		     * If we have precisely two undecided squares
		     * and precisely one line to place between
		     * them, _and_ those squares are adjacent, then
		     * we can mark them as equivalent to one
		     * another.
		     * 
		     * This even applies if meq >= 0: if we have a
		     * 2 clue point and two of its neighbours are
		     * already marked equivalent, we can indeed
		     * mark the other two as equivalent.
		     * 
		     * We don't bother with this on DIFF_EASY,
		     * since we wouldn't have used the results
		     * anyway.
		     */
		    last = -1;
		    for (i = 0; i < nneighbours; i++) {
			j = neighbours[i].pos;
			if (soln[j] == 0 && j != mj1 && j != mj2) {
			    if (last < 0)
				last = i;
			    else if (last == i-1 || (last == 0 && i == 3))
				break; /* found a pair */
			}
		    }
		    if (i < nneighbours) {
			int sv1, sv2;

			assert(last >= 0);
			/*
			 * neighbours[last] and neighbours[i] are
			 * the pair. Mark them equivalent.
			 */
			mj1 = neighbours[last].pos;
			mj2 = neighbours[i].pos;
			mj1 = dsf_canonify(sc->equiv, mj1);
			sv1 = sc->slashval[mj1];
			mj2 = dsf_canonify(sc->equiv, mj2);
			sv2 = sc->slashval[mj2];
			if (sv1 != 0 && sv2 != 0 && sv1 != sv2) {
			    return 0;
			}
			sv1 = sv1 ? sv1 : sv2;
			dsf_merge(sc->equiv, mj1, mj2);
			mj1 = dsf_canonify(sc->equiv, mj1);
			sc->slashval[mj1] = sv1;
		    }
		}
	    }

	if (done_something)
	    continue;

	/*
	 * Failing that, we now apply the second condition, which
	 * is that no square may be filled in such a way as to form
	 * a loop. Also in this loop (since it's over squares
	 * rather than points), we check slashval to see if we've
	 * already filled in another square in the same equivalence
	 * class.
	 * 
	 * The slashval check is disabled on DIFF_EASY, as is dead
	 * end avoidance. Only _immediate_ loop avoidance remains.
	 */
	for (y = 0; y < h; y++)
	    for (x = 0; x < w; x++) {
		bool fs, bs;
                int v, c1, c2;

		if (soln[y*w+x])
		    continue;	       /* got this one already */

		fs = false;
		bs = false;

		if (difficulty > DIFF_EASY)
		    v = sc->slashval[dsf_canonify(sc->equiv, y*w+x)];
		else
		    v = 0;

		/*
		 * Try to rule out connectivity between (x,y) and
		 * (x+1,y+1); if successful, we will deduce that we
		 * must have a forward slash.
		 */
		c1 = dsf_canonify(sc->connected, y*W+x);
		c2 = dsf_canonify(sc->connected, (y+1)*W+(x+1));
		if (c1 == c2) {
		    fs = true;
		}
		if (v == +1) {
		    fs = true;
		}

		/*
		 * Now do the same between (x+1,y) and (x,y+1), to
		 * see if we are required to have a backslash.
		 */
		c1 = dsf_canonify(sc->connected, y*W+(x+1));
		c2 = dsf_canonify(sc->connected, (y+1)*W+x);
		if (c1 == c2) {
		    bs = true;
		}
		if (v == -1) {
		    bs = true;
		}

		if (fs && bs) {
		    /*
		     * No consistent value for this at all!
		     */
		    return 0;          /* impossible */
		}

		if (fs) {
		    fill_square(w, h, x, y, +1, soln, sc->connected, sc);
		    done_something = true;
		} else if (bs) {
		    fill_square(w, h, x, y, -1, soln, sc->connected, sc);
		    done_something = true;
		}
	    }

	if (done_something)
	    continue;

    } while (done_something);

    /*
     * Solver can make no more progress. See if the grid is full.
     */
    for (i = 0; i < w*h; i++)
	if (!soln[i])
	    return 2;		       /* failed to converge */
    return 1;			       /* success */
}
