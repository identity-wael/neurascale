import { defineField, defineType } from 'sanity';

export const contact = defineType({
  name: 'contact',
  title: 'Contact Section',
  type: 'document',
  fields: [
    defineField({
      name: 'sectionTitle',
      title: 'Section Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'introduction',
      title: 'Introduction',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'contactChannels',
      title: 'Contact Channels',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'email',
              title: 'Email',
              type: 'string',
              validation: (Rule) => Rule.required().email(),
            }),
            defineField({
              name: 'description',
              title: 'Description',
              type: 'text',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'iconType',
              title: 'Icon Type',
              type: 'string',
              options: {
                list: [
                  { title: 'Chat', value: 'chat' },
                  { title: 'Code', value: 'code' },
                  { title: 'Academic', value: 'academic' },
                  { title: 'Document', value: 'document' },
                ],
              },
            }),
            defineField({
              name: 'responseTime',
              title: 'Response Time',
              type: 'string',
            }),
          ],
        },
      ],
    }),
    defineField({
      name: 'formSubjects',
      title: 'Form Subject Options',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'value',
              title: 'Value',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'label',
              title: 'Label',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
          ],
        },
      ],
    }),
    defineField({
      name: 'officeLocation',
      title: 'Office Location',
      type: 'object',
      fields: [
        defineField({
          name: 'city',
          title: 'City',
          type: 'string',
        }),
        defineField({
          name: 'address',
          title: 'Address',
          type: 'text',
        }),
        defineField({
          name: 'focus',
          title: 'Focus',
          type: 'string',
        }),
        defineField({
          name: 'coordinates',
          title: 'Coordinates',
          type: 'object',
          fields: [
            defineField({
              name: 'lat',
              title: 'Latitude',
              type: 'number',
            }),
            defineField({
              name: 'lng',
              title: 'Longitude',
              type: 'number',
            }),
          ],
        }),
      ],
    }),
  ],
  preview: {
    select: {
      title: 'sectionTitle',
    },
  },
});

export default contact;
