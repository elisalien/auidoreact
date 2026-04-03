// ─── KALEIDOSCOPE GÉOMÉTRIQUE ───
// params: (segments, inner_zoom, rotation_speed, shape_complexity)

float shape(vec2 p, float complexity) {
    float d = 1e5;
    // Layered geometric shapes
    float r = length(p);
    float a = atan(p.y, p.x);

    // Circles
    d = min(d, abs(r - 0.3 - sin(u_time * u_speed * 0.5) * 0.1));
    d = min(d, abs(r - 0.6 - cos(u_time * u_speed * 0.3) * 0.05));

    // Polygon edges
    float sides = 3.0 + floor(complexity);
    float angle = 6.28318 / sides;
    float sector = mod(a + 3.14159, angle) - angle * 0.5;
    float poly = r * cos(sector) - 0.4;
    d = min(d, abs(poly));

    // Rotating lines
    for (float i = 0.0; i < 4.0; i++) {
        float la = i * 3.14159 / 4.0 + u_time * u_speed * 0.2;
        vec2 dir = vec2(cos(la), sin(la));
        d = min(d, abs(dot(p, dir)));
    }

    return d;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv - 0.5) * 2.0;
    float aspect = u_resolution.x / u_resolution.y;
    p.x *= aspect;

    float segments = u_params.x + u_bass * 4.0;
    float zoom = u_params.y + u_mid * 0.5;
    float rot_speed = u_params.z;
    float complexity = u_params.w + u_high * 2.0;

    // Polar coordinates
    float r = length(p);
    float a = atan(p.y, p.x);

    // Rotation from audio
    a += u_time * u_speed * rot_speed + u_beat * 0.5;

    // Kaleidoscope mirror
    float seg_angle = 6.28318 / segments;
    a = mod(a, seg_angle);
    a = abs(a - seg_angle * 0.5);

    // Back to cartesian in kaleidoscope space
    vec2 kp = vec2(cos(a), sin(a)) * r * zoom;

    // Inner pattern
    float d = shape(kp, complexity);

    // Secondary FBM layer
    float n = fbm(kp * 3.0 + u_time * u_speed * 0.1, 4);

    // Color
    float edge = smoothstep(0.02, 0.0, d);
    float glow = 0.01 / (d + 0.01);
    float pattern = n * 0.5 + 0.5;

    vec3 col = u_color1 * pattern * 0.3;
    col += u_color2 * glow * 0.15;
    col += u_color3 * edge * (0.5 + u_rms * 0.5);

    // Radial color gradient
    col = mix(col, u_color2 * 0.5, smoothstep(0.8, 1.5, r));

    // Audio pulse
    col += u_color3 * u_beat * 0.2 * (1.0 - r);

    // Vignette
    float vig = 1.0 - 0.5 * r;
    col *= max(vig, 0.0);

    // Feedback
    vec3 prev = texture(u_feedback, uv).rgb;
    col = mix(col, prev, u_feedback_amt);

    fragColor = vec4(col, 1.0);
}
