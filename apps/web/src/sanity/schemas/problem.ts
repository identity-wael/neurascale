import { defineField, defineType } from 'sanity';

export const problem = defineType({
  name: 'problem',
  title: 'Problem Section',
  type: 'document',
  fields: [
    defineField({
      name: 'sectionHeader',
      title: 'Section Header',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'subtitle',
      title: 'Subtitle',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'coreArchitecture',
      title: 'Core Architecture',
      type: 'object',
      fields: [
        defineField({
          name: 'title',
          title: 'Title',
          type: 'string',
        }),
        defineField({
          name: 'description',
          title: 'Description',
          type: 'text',
        }),
        defineField({
          name: 'layers',
          title: 'Architecture Layers',
          type: 'array',
          of: [
            {
              type: 'object',
              fields: [
                { name: 'name', title: 'Name', type: 'string' },
                { name: 'description', title: 'Description', type: 'string' },
              ],
            },
          ],
        }),
      ],
    }),
    defineField({
      name: 'processingSpecs',
      title: 'Processing Specifications',
      type: 'object',
      fields: [
        defineField({
          name: 'title',
          title: 'Title',
          type: 'string',
        }),
        defineField({
          name: 'specs',
          title: 'Specifications',
          type: 'array',
          of: [
            {
              type: 'object',
              fields: [
                { name: 'label', title: 'Label', type: 'string' },
                { name: 'value', title: 'Value', type: 'string' },
              ],
            },
          ],
        }),
      ],
    }),
    defineField({
      name: 'computingPower',
      title: 'Computing Power',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'spec', title: 'Specification', type: 'string' },
            { name: 'description', title: 'Description', type: 'string' },
          ],
        },
      ],
    }),
    defineField({
      name: 'aimlIntegration',
      title: 'AI/ML Integration',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'neuralIdentity',
      title: 'Neural Identity',
      type: 'object',
      fields: [
        { name: 'title', title: 'Title', type: 'string' },
        { name: 'description', title: 'Description', type: 'text' },
      ],
    }),
    defineField({
      name: 'openSourceFeatures',
      title: 'Open Source Features',
      type: 'array',
      of: [{ type: 'string' }],
    }),
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
});

export default problem;
