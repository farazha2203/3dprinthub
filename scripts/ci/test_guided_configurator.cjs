const assert = require('node:assert/strict');
const test = require('node:test');
const core = require('../../static/store/js/phase50-profile-selector.js');
const make = (id, size, color, material, quality, extra = {}) => ({
    id, size, color, material, quality, orderable: true,
    finalWeight: 100, printMinutes: 60, price: 100000, ...extra,
});
const variants = [
    make('1', '20', 'Red', 'PLA', 'Normal'),
    make('2', '20', 'Red', 'PETG', 'Fine', {price: 200000}),
    make('3', '20', 'Blue', 'PLA', 'Normal'),
    make('4', '30', 'Blue', 'PETG', 'Fine'),
    make('5', '30', 'Green', 'PLA', 'Normal', {orderable: false}),
];
const selected = (variant) => Object.fromEntries(core.GUIDED_DIMENSIONS.map(dim => [dim, core.valueFor(variant, dim)]));

test('only the upstream prefix filters colors and compatible materials', () => {
    const state = selected(variants[0]);
    const colors = core.variantsForDimension(variants, state, core.GUIDED_DIMENSIONS, 1);
    assert.deepEqual(colors.map(v => v.id), ['1', '2', '3']);
    const materials = core.variantsForDimension(variants, state, core.GUIDED_DIMENSIONS, 2);
    assert.deepEqual(materials.map(v => v.material), ['PLA', 'PETG']);
    assert.equal(core.resolveGuidedVariant(variants, state).id, '1');
});
test('an upstream change invalidates the previous canonical variant', () => {
    const state = {...selected(variants[0]), variant: '1', size: '30'};
    core.clearDownstreamState(state, [...core.GUIDED_DIMENSIONS, 'variant'], 0);
    assert.equal(core.resolveGuidedVariant(variants, state), null);
    core.fillGuidedSingletons(variants, state);
    assert.equal(core.resolveGuidedVariant(variants, state).id, '4');
});
test('singletons never fill past an unresolved step', () => {
    const state = {};
    core.fillGuidedSingletons(variants, state);
    assert.deepEqual(state, {});
    state.size = '20';
    core.fillGuidedSingletons(variants, state);
    assert.deepEqual(state, {size: '20'});
});
test('unavailable combinations never resolve and invalid prefixes never broaden', () => {
    assert.equal(core.resolveGuidedVariant(variants, selected(variants[4])), null);
    const state = {...selected(variants[0]), size: 'missing'};
    assert.deepEqual(core.variantsForDimension(variants, state, core.GUIDED_DIMENSIONS, 1), []);
});
test('duplicate four-step paths require explicit canonical choice, preserving brand and weight', () => {
    const other = {...variants[0], id: 'other', filamentBrand: 'Other', finalWeight: 200, price: 900000};
    const pool = [variants[0], other];
    const state = selected(variants[0]);
    assert.equal(core.resolveGuidedVariant(pool, state), null);
    state.variant = 'other';
    assert.equal(core.resolveGuidedVariant(pool, state), other);
});
test('same visual color spans materials but finish/palette remain distinct', () => {
    assert.equal(core.valueFor(variants[0], 'color'), core.valueFor(variants[1], 'color'));
    assert.notEqual(core.valueFor(variants[0], 'color'), core.valueFor({...variants[0], colorFinish: 'glossy'}, 'color'));
});
test('missing optional size/color still resolves an ordinary native variant', () => {
    const pool = [make('plain', '', '', 'PLA', 'Normal')];
    const state = {};
    core.fillGuidedSingletons(pool, state);
    assert.equal(core.resolveGuidedVariant(pool, state).id, 'plain');
});
test('API metadata preserves canonical zero price instead of stale native price', () => {
    const variant = core.readNativeOption({value: '1', dataset: {total: '900'}, textContent: 'Native'}, {unit_price: 0, orderable: false});
    assert.equal(variant.price, 0);
    assert.equal(variant.orderable, false);
});
