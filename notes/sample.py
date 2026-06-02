graph {
    V: vertices* string;
    E: edges* char[malloc(sizeof(char) * 2)];
}

vertex {
    v: value* bitstring;
    c: cardinality size_t;
}

edge {
    e: edge* bitstring;
}

bit* sample (g: graph graph, t: time size_t) {
    int live = 0;
    sample = parse(g); // see mlql
    Y = measure_error(input, sample); // this is an audio sample
    dY = Y / t;
    ddY = dY / v.c for v in g // cardinality predicts liveliness
    for (size_t i = 0; i < TIMEOUT, i++) {
        if (Y > dY) {
            input[i] = sample[i] - ddY; // update memory for workers
        } // only curious workers get input
        else {
            live = -1;
        }
    }
    save_meta(live, sample, Y, dY, ddY); // TODO: format

    // bootstrap her
    if is_pressed(/dev/input) input[i]++;
}
