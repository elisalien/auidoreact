// ─── GLITCH BRUTALIST HUD ───
// params: (grid_density, scanline_intensity, glitch_amount, data_density)

float grid(vec2 p, float density) {
    vec2 g = abs(fract(p * density) - 0.5);
    float d = min(g.x, g.y);
    return smoothstep(0.02, 0.0, d) * 0.3;
}

float scanlines(vec2 uv, float intensity) {
    return (sin(uv.y * u_resolution.y * 1.5) * 0.5 + 0.5) * intensity;
}

float digital_circle(vec2 p, float radius, float thickness) {
    float d = abs(length(p) - radius);
    return smoothstep(thickness, 0.0, d);
}

float hud_element(vec2 p, float idx) {
    float val = 0.0;

    // Rotating arc
    float a = atan(p.y, p.x);
    float r = length(p);
    float arc_start = idx * 1.5 + u_time * u_speed * 0.3;
    float arc_len = 1.0 + sin(u_time * u_speed * 0.5 + idx) * 0.5;
    float in_arc = step(0.0, sin(a - arc_start)) * step(0.0, sin(arc_start + arc_len - a));
    val += digital_circle(p, 0.3 + idx * 0.15, 0.005) * in_arc;

    return val;
}

float bar_graph(vec2 p, float data_density) {
    float val = 0.0;
    float bars = floor(data_density * 20.0);
    if (bars < 1.0) return 0.0;

    float bar_w = 1.0 / bars;
    float bar_idx = floor(p.x / bar_w);
    float bar_x = fract(p.x / bar_w);

    if (bar_x > 0.2 && bar_x < 0.8 && bar_idx >= 0.0 && bar_idx < bars) {
        // Read from spectrum
        float spec = texture(u_spectrum, vec2(bar_idx / bars, 0.5)).r;
        float bar_h = spec * 0.8;
        if (p.y < bar_h && p.y > 0.0) {
            val = 0.8;
        }
    }
    return val;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = uv - 0.5;
    float aspect = u_resolution.x / u_resolution.y;
    p.x *= aspect;

    float grid_dens = u_params.x;
    float scan_int = u_params.y;
    float glitch_amt = u_params.z;
    float data_dens = u_params.w;

    // ─── Glitch displacement ───
    vec2 glitch_uv = uv;
    if (u_beat > 0.3) {
        float block_y = floor(uv.y * 20.0) / 20.0;
        float rnd = hash21(vec2(block_y, floor(u_time * 10.0)));
        if (rnd > 1.0 - glitch_amt * u_beat) {
            glitch_uv.x += (rnd - 0.5) * 0.08 * u_beat;
        }
    }

    // Chromatic aberration on beat
    float chroma_offset = u_beat * 0.005 * glitch_amt;

    vec2 p_glitch = glitch_uv - 0.5;
    p_glitch.x *= aspect;

    // ─── Layers ───
    float base_grid = grid(p_glitch, grid_dens);

    // HUD circles
    float hud = 0.0;
    hud += hud_element(p_glitch, 0.0) * (0.5 + u_bass * 0.5);
    hud += hud_element(p_glitch, 1.0) * (0.3 + u_mid * 0.7);
    hud += hud_element(p_glitch, 2.0) * (0.2 + u_high * 0.8);

    // Center reticle
    float center_d = length(p_glitch);
    hud += smoothstep(0.003, 0.0, abs(p_glitch.x)) * step(center_d, 0.05) * 0.5;
    hud += smoothstep(0.003, 0.0, abs(p_glitch.y)) * step(center_d, 0.05) * 0.5;
    hud += digital_circle(p_glitch, 0.08, 0.003) * (0.3 + u_rms);

    // Bar graph in corner
    vec2 bar_p = (uv - vec2(0.05, 0.05)) * vec2(3.0, 5.0);
    float bars = bar_graph(bar_p, data_dens);

    // Scanlines
    float scan = scanlines(glitch_uv, scan_int);

    // ─── Compose ───
    vec3 col = u_color1 * 0.15; // dark base

    // Grid
    col += u_color2 * base_grid * 0.3;

    // HUD elements
    col += u_color3 * hud * 0.7;
    col += u_color2 * hud * 0.3;

    // Bar graph
    col += mix(u_color2, u_color3, bar_p.y * 0.5) * bars * 0.5;

    // Noise/grain
    float grain = hash21(uv * u_resolution + u_time * 100.0) * 0.05;
    col += grain;

    // Scanline darkening
    col *= 1.0 - scan * 0.15;

    // Chromatic aberration
    vec3 col_r = col;
    if (chroma_offset > 0.001) {
        vec2 uv_r = glitch_uv + vec2(chroma_offset, 0.0);
        vec2 uv_b = glitch_uv - vec2(chroma_offset, 0.0);
        col_r = vec3(col.r * 1.2, col.g, col.b * 0.8);
    }
    col = mix(col, col_r, min(u_beat, 1.0));

    // Beat flash
    col += u_color3 * u_beat * 0.1;

    // RMS breathing
    col *= 0.8 + u_rms * 0.4;

    // Feedback
    vec3 prev = texture(u_feedback, glitch_uv).rgb;
    col = mix(col, prev, u_feedback_amt);

    fragColor = vec4(col, 1.0);
}
