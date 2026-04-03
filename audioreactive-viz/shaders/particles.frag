// ─── PARTICLE CONSTELLATION FIELD ───
// params: (density, trail_length, glow_size, connection_dist)

float particle_field(vec2 p, float density, float glow) {
    float val = 0.0;
    vec2 id = floor(p);
    vec2 f = fract(p);

    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 cell_id = id + neighbor;
            float rnd = hash21(cell_id);

            if (rnd > density) continue;

            // Animated position within cell
            float phase = rnd * 6.28;
            float speed = 0.3 + rnd * 0.5;
            vec2 offset = vec2(
                sin(u_time * u_speed * speed + phase) * 0.3,
                cos(u_time * u_speed * speed * 0.7 + phase * 1.3) * 0.3
            );
            offset += u_beat * (hash22(cell_id) * 0.2);

            vec2 point = neighbor + 0.5 + offset - f;
            float d = length(point);

            // Glow
            val += glow / (d * d + 0.001);
        }
    }
    return val;
}

float connections(vec2 p, float density, float max_dist) {
    float val = 0.0;
    vec2 id = floor(p);
    vec2 f = fract(p);

    // Find closest 2 points and draw line between them
    float d1 = 100.0, d2 = 100.0;
    vec2 p1, p2;

    for (int y = -2; y <= 2; y++) {
        for (int x = -2; x <= 2; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 cell_id = id + neighbor;
            float rnd = hash21(cell_id);
            if (rnd > density) continue;

            float phase = rnd * 6.28;
            float speed = 0.3 + rnd * 0.5;
            vec2 offset = vec2(
                sin(u_time * u_speed * speed + phase) * 0.3,
                cos(u_time * u_speed * speed * 0.7 + phase * 1.3) * 0.3
            );
            vec2 point = neighbor + 0.5 + offset - f;
            float d = length(point);

            if (d < d1) { d2 = d1; p2 = p1; d1 = d; p1 = point; }
            else if (d < d2) { d2 = d; p2 = point; }
        }
    }

    // Line between two closest points
    if (d1 < max_dist && d2 < max_dist) {
        vec2 ba = p2 - p1;
        float t_line = clamp(dot(-p1, ba) / dot(ba, ba), 0.0, 1.0);
        float dist_to_line = length(p1 + ba * t_line);
        float line_len = length(ba);
        if (line_len < max_dist * 2.0) {
            val = 0.003 / (dist_to_line + 0.002) * (1.0 - line_len / (max_dist * 2.0));
        }
    }
    return val;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = uv * 8.0 + u_bass * 0.5;
    float aspect = u_resolution.x / u_resolution.y;
    p.x *= aspect;

    float density = u_params.x + u_rms * 0.2;
    float glow = u_params.z + u_high * 0.02;
    float conn_dist = u_params.w + u_mid * 0.1;

    // Particle glow
    float particles = particle_field(p, density, glow);

    // Connection lines
    float lines = connections(p, density, conn_dist) * (0.5 + u_mid);

    // Color
    float intensity = particles + lines;
    vec3 col = u_color1 * 0.1; // base background
    col += u_color2 * particles * 0.8;
    col += u_color3 * lines * 2.0;
    col += u_color3 * u_beat * particles * 0.5;

    // Tone mapping
    col = col / (col + 0.8);

    // Feedback (trails)
    vec3 prev = texture(u_feedback, uv).rgb;
    col = max(col, prev * u_feedback_amt);

    fragColor = vec4(col, 1.0);
}
