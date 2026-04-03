// ─── FLUID NOISE LANDSCAPES ───
// params: (octaves_intensity, warp_amount, height_scale, color_spread)

void main() {
    float t = u_time * u_speed;
    vec2 uv = v_uv;
    vec2 p = (uv - 0.5) * 3.0;
    float aspect = u_resolution.x / u_resolution.y;
    p.x *= aspect;

    float octaves = u_params.x;
    float warp = u_params.y + u_bass * 1.5;
    float height = u_params.z + u_mid * 0.5;
    float spread = u_params.w;

    // Domain warping — 2 passes for organic feel
    vec2 q = vec2(
        fbm(p + vec2(0.0, 0.0) + t * 0.1, int(octaves)),
        fbm(p + vec2(5.2, 1.3) + t * 0.12, int(octaves))
    );

    vec2 r = vec2(
        fbm(p + warp * q + vec2(1.7, 9.2) + t * 0.08, int(octaves)),
        fbm(p + warp * q + vec2(8.3, 2.8) + t * 0.1, int(octaves))
    );

    float f = fbm(p + warp * r + u_beat * 0.3, int(octaves));

    // Height displacement from audio
    f += u_bass * height * 0.3;
    f += sin(f * 6.0 + t) * u_high * 0.15;

    // Color mapping
    float c = f * spread + 0.5;
    vec3 col = palette(c, u_color1, u_color2, u_color3);

    // Luminance modulation from audio
    col += u_color3 * u_beat * 0.3;
    col *= 0.8 + u_rms * 0.4;

    // Subtle vignette
    float vig = 1.0 - 0.4 * length(uv - 0.5);
    col *= vig;

    // Feedback blend
    vec3 prev = texture(u_feedback, uv).rgb;
    col = mix(col, prev, u_feedback_amt);

    fragColor = vec4(col, 1.0);
}
